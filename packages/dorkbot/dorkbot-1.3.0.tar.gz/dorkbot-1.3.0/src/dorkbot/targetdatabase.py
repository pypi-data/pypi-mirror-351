#!/usr/bin/env python3
if __package__:
    from dorkbot.database import Database
    from dorkbot.target import Target
    from dorkbot.util import generate_fingerprint, get_parsed_url
else:
    from database import Database
    from target import Target
    from util import generate_fingerprint, get_parsed_url
import logging
import os


class TargetDatabase(Database):
    def __init__(self, address, drop_tables=False, create_tables=False, retries=0, retry_on=[]):
        protocols = ["postgresql://", "sqlite3://"]
        if not any(address.startswith(protocol) for protocol in protocols):
            address = f"sqlite3://{address}"
        Database.__init__(self, address, retries, retry_on)

        if self.database and address.startswith("sqlite3://"):
            try:
                os.makedirs(os.path.dirname(os.path.abspath(self.database)), exist_ok=True)
            except OSError as e:
                logging.error(f"Failed to create parent directory for database file - {str(e)}")
                raise

        self.connect()

        if drop_tables:
            logging.debug("Dropping tables")
            self.execute("DROP TABLE IF EXISTS targets")
            self.execute("DROP TABLE IF EXISTS sources")
            self.execute("DROP TABLE IF EXISTS fingerprints")
            self.execute("DROP TABLE IF EXISTS blocklist")

        if create_tables:
            self.execute("CREATE TABLE IF NOT EXISTS targets"
                         f" (id {self.id_type},"
                         " url VARCHAR UNIQUE,"
                         " source_id INTEGER,"
                         " fingerprint_id INTEGER,"
                         " scanned INTEGER DEFAULT 0)")
            self.execute("CREATE TABLE IF NOT EXISTS sources"
                         f" (id {self.id_type},"
                         " source VARCHAR UNIQUE)")
            self.execute("CREATE TABLE IF NOT EXISTS fingerprints"
                         f" (id {self.id_type},"
                         " fingerprint VARCHAR UNIQUE,"
                         " scanned INTEGER DEFAULT 0)")
            self.execute("CREATE TABLE IF NOT EXISTS blocklist"
                         f" (id {self.id_type},"
                         " item VARCHAR UNIQUE)")

    def get_urls(self, args):
        if args.source and args.source is not True:
            sql = "SELECT t.url FROM targets t" \
                  + " INNER JOIN sources s on s.id = t.source_id"
        elif args.source is True:
            sql = "SELECT t.url, s.source FROM targets t" \
                  + " LEFT JOIN sources s on s.id = t.source_id"
        else:
            sql = "SELECT t.url FROM targets t"

        if args.list_unscanned:
            sql += " LEFT JOIN fingerprints f on f.id = t.fingerprint_id" \
                + " WHERE t.scanned = '0' AND (t.fingerprint_id IS NULL OR f.scanned = '0')"

        if args.source and args.source is not True:
            if args.list_unscanned:
                sql += " AND s.source = %s" % self.param
            else:
                sql += " WHERE s.source = %s" % self.param
            parameters = (args.source,)
        else:
            parameters = ()

        if args.random:
            sql += " ORDER BY RANDOM()"
        else:
            sql += " ORDER BY t.id ASC"

        if args.count > 0:
            sql += f" LIMIT {args.count}"

        rows = self.execute(sql, parameters, fetch=True)
        urls = [" | ".join([str(column or "") for column in row]) for row in rows] if rows else []
        return urls

    def get_unscanned_query(self, args, count=-1):
        sql = "SELECT t.url, t.id, f.id, f.fingerprint FROM targets t"
        if args.source and args.source is not True:
            sql += " INNER JOIN sources s on s.id = t.source_id"
        sql += " LEFT JOIN fingerprints f on f.id = t.fingerprint_id" \
            + " WHERE t.scanned = '0' AND (t.fingerprint_id IS NULL OR f.scanned = '0')"
        if args.source and args.source is not True:
            sql += " AND s.source = %s" % self.param
            parameters = (args.source,)
        else:
            parameters = ()
        if args.random:
            sql += " ORDER BY RANDOM()"
        else:
            sql += " ORDER BY t.id ASC"

        if count > 0:
            sql += f" LIMIT {args.count}"
        return sql, parameters

    def get_next_target(self, args, blocklists=[]):
        sql, parameters = self.get_unscanned_query(args)
        target = None
        fingerprints = {}
        while True:
            row = self.execute(sql, parameters, fetch=1)
            if not row:
                break
            url, target_id, fingerprint_id, fingerprint = row

            if True in [blocklist.match(Target(url)) for blocklist in blocklists]:
                logging.debug(f"Deleting (matches blocklist pattern): {url}")
                self.delete_target(url)

            elif fingerprint_id:
                logging.debug(f"Found unique fingerprint: {url}")
                if not args.test:
                    self.mark_fingerprint_scanned(fingerprint_id)
                target = url

            else:
                logging.debug(f"Computing fingerprint: {url}")
                fingerprint = generate_fingerprint(url)

                if fingerprint in fingerprints:
                    logging.debug(f"Skipping (matches existing fingerprint): {url}")
                    fingerprint_id = fingerprints[fingerprint]
                else:
                    fingerprint_id = self.get_fingerprint_id(fingerprint)
                    if fingerprint_id:
                        logging.debug(f"Skipping (matches scanned fingerprint): {url}")
                        fingerprints[fingerprint] = fingerprint_id
                    else:
                        logging.debug(f"Found unique fingerprint: {url}")
                        fingerprint_id = self.add_fingerprint(fingerprint, scanned=(not args.test))
                        target = url
                self.update_target_fingerprint(target_id, fingerprint_id)

            if target:
                break
        return target

    def add_target(self, url, source=None, blocklists=[]):
        if True in [blocklist.match(Target(url)) for blocklist in blocklists]:
            logging.debug(f"Ignoring (matches blocklist pattern): {url}")
            return

        logging.debug(f"Adding target {url}")
        if source:
            source_id = self.get_source_id(source)
            if not source_id:
                source_id = self.add_source(source)
        else:
            source_id = None

        self.execute("%s INTO targets (url, source_id) VALUES (%s, %s) %s"
                     % (self.insert, self.param, self.param, self.conflict),
                     (get_parsed_url(url), source_id))

    def add_targets(self, urls, source=None, blocklists=[], chunk_size=1000):
        logging.debug(f"Adding {len(urls)} targets")
        if source:
            source_id = self.get_source_id(source)
            if not source_id:
                source_id = self.add_source(source)
        else:
            source_id = None

        for x in range(0, len(urls), chunk_size):
            urls_chunk = urls[x:x + chunk_size]
            urls_chunk_add = []
            for url in urls_chunk:
                if True in [blocklist.match(Target(url)) for blocklist in blocklists]:
                    logging.debug(f"Ignoring (matches blocklist pattern): {url}")
                else:
                    urls_chunk_add.append(get_parsed_url(url))

            self.execute("%s INTO targets (url, source_id) VALUES (%s, %s) %s"
                         % (self.insert, self.param, self.param, self.conflict),
                         [(url, source_id) for url in urls_chunk_add])

    def mark_target_scanned(self, target_id):
        self.execute("UPDATE targets SET scanned = 1 WHERE id = %s" % self.param, (target_id,))

    def delete_target(self, url):
        logging.debug(f"Deleting target {url}")
        self.execute("DELETE FROM targets WHERE url = %s" % self.param, (url,))

    def flush_targets(self):
        logging.info("Flushing targets")
        self.execute("DELETE FROM targets")
        self.execute("DELETE FROM sources")

    def add_source(self, source):
        logging.debug(f"Adding source {source}")
        row = self.execute("%s INTO sources (source) VALUES (%s) %s RETURNING id"
                           % (self.insert, self.param, self.conflict),
                           (source,), fetch=1)
        return row if not row else row[0]

    def get_source_id(self, source):
        row = self.execute("SELECT id FROM sources WHERE source = %s"
                           % self.param, (source,), fetch=1)
        return row if not row else row[0]

    def get_sources(self):
        rows = self.execute("SELECT source FROM sources ORDER BY id ASC", fetch=True)
        return [row[0] for row in rows] if rows else []

    def add_fingerprint(self, fingerprint, scanned=False):
        logging.debug(f"Adding fingerprint {fingerprint}")
        row = self.execute("%s INTO fingerprints (fingerprint, scanned) VALUES (%s, %s) %s RETURNING id"
                           % (self.insert, self.param, self.param, self.conflict),
                           (fingerprint, 1 if scanned else 0), fetch=1)
        return row if not row else row[0]

    def update_target_fingerprint(self, target_id, fingerprint_id):
        logging.debug(f"Updating target fingerprint id {target_id}->{fingerprint_id}")
        self.execute("UPDATE targets SET fingerprint_id = %s WHERE id = %s"
                     % (self.param, self.param), (fingerprint_id, target_id))

    def flush_fingerprints(self):
        logging.info("Flushing fingerprints")
        self.execute("UPDATE targets SET fingerprint_id = NULL")
        self.execute("DELETE FROM fingerprints")

    def reset_scanned(self):
        logging.info("Resetting scanned")
        self.execute("UPDATE targets SET scanned = 0")
        self.execute("UPDATE fingerprints SET scanned = 0")

    def get_fingerprint_id(self, fingerprint):
        row = self.execute("SELECT id FROM fingerprints WHERE fingerprint = %s"
                           % self.param, (fingerprint,), fetch=1)
        return row if not row else row[0]

    def mark_fingerprint_scanned(self, fingerprint_id):
        self.execute("UPDATE fingerprints SET scanned = 1 WHERE id = %s" % self.param, (fingerprint_id,))

    def prune(self, blocklists, args):
        logging.info("Pruning database")
        sql, parameters = self.get_unscanned_query(args, count=args.count)
        targets = self.execute(sql, parameters, fetch=True)
        if not targets:
            return
        targets.reverse()
        fingerprints = {}
        while targets:
            url, target_id, fingerprint_id, fingerprint = targets.pop()

            if True in [blocklist.match(Target(url)) for blocklist in blocklists]:
                logging.debug(f"Deleting (matches blocklist pattern): {url}")
                self.delete_target(url)

            elif fingerprint_id:
                if fingerprint in fingerprints:
                    logging.debug(f"Skipping (matches existing fingerprint): {url}")
                    self.mark_target_scanned(target_id)
                else:
                    logging.debug(f"Found unique fingerprint: {url}")
                    fingerprints[fingerprint] = fingerprint_id

            else:
                logging.debug(f"Computing fingerprint: {url}")
                fingerprint = generate_fingerprint(url)

                if fingerprint in fingerprints:
                    logging.debug(f"Skipping (matches existing fingerprint): {url}")
                    fingerprint_id = fingerprints[fingerprint]
                    self.mark_target_scanned(target_id)
                else:
                    fingerprint_id = self.get_fingerprint_id(fingerprint)
                    if fingerprint_id:
                        logging.debug(f"Skipping (matches existing fingerprint): {url}")
                    else:
                        logging.debug(f"Found unique fingerprint: {url}")
                        fingerprint_id = self.add_fingerprint(fingerprint, scanned=False)
                    fingerprints[fingerprint] = fingerprint_id

                self.update_target_fingerprint(target_id, fingerprint_id)

    def get_fingerprintless_query(self, args):
        sql = "SELECT t.url, t.id FROM targets t"
        if args.source and args.source is not True:
            sql += " INNER JOIN sources s on s.id = t.source_id"
        sql += " WHERE t.fingerprint_id IS NULL"
        if args.source and args.source is not True:
            sql += " AND s.source = %s" % self.param
            parameters = (args.source,)
        else:
            parameters = ()
        if args.count > 0:
            sql += f" LIMIT {args.count}"
        return sql, parameters

    def generate_fingerprints(self, args):
        logging.info("Generating fingerprints")
        sql, parameters = self.get_fingerprintless_query(args)
        targets = self.execute(sql, parameters, fetch=True)
        if targets:
            targets.reverse()
        fingerprints = {}
        while targets:
            url, target_id = targets.pop()
            fingerprint = generate_fingerprint(url)
            if fingerprint in fingerprints:
                fingerprint_id = fingerprints[fingerprint]
            else:
                fingerprint_id = self.get_fingerprint_id(fingerprint)
                if fingerprint_id:
                    fingerprints[fingerprint] = fingerprint_id
                else:
                    fingerprint_id = self.add_fingerprint(fingerprint, scanned=False)
                    fingerprints[fingerprint] = fingerprint_id
            self.update_target_fingerprint(target_id, fingerprint_id)

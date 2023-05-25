import logging

logger = logging.getLogger(__name__)

class MasterSlaveRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'admin' or \
                model._meta.app_label == 'sessions' or \
                model._meta.app_label == 'sites' or \
                model._meta.app_label == 'auth':
            logger.info(f"Admin operation(admin, sessions, sites, auth) for model {model.__name__} is routed to 'default' database")
            return 'default'

        logger.info(f"Read operation for model {model.__name__} is routed to 'slave' database")
        return 'slave'


    def db_for_write(self, model, **hints):
        logger.info(f"Write operation for model {model.__name__} is routed to 'default' database")
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'

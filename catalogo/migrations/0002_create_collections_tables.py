from django.db import migrations


CREATE_COLLECTION_TABLE = r'''
CREATE TABLE IF NOT EXISTS catalogo_collection (
    id BIGSERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED,
    name VARCHAR(150) NOT NULL,
    description TEXT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_collection_per_user_name_idx
    ON catalogo_collection (owner_id, name);
'''


DROP_COLLECTION_TABLE = r'''
DROP TABLE IF EXISTS catalogo_collection CASCADE;
'''


CREATE_COLLECTIONITEM_TABLE = r'''
CREATE TABLE IF NOT EXISTS catalogo_collectionitem (
    id BIGSERIAL PRIMARY KEY,
    collection_id BIGINT NOT NULL REFERENCES catalogo_collection(id) DEFERRABLE INITIALLY DEFERRED,
    muestra_id BIGINT NOT NULL REFERENCES catalogo_muestrabiologica(id) DEFERRABLE INITIALLY DEFERRED,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS uniq_item_per_collection_idx
    ON catalogo_collectionitem (collection_id, muestra_id);
'''


DROP_COLLECTIONITEM_TABLE = r'''
DROP TABLE IF EXISTS catalogo_collectionitem CASCADE;
'''


class Migration(migrations.Migration):
    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(sql=CREATE_COLLECTION_TABLE, reverse_sql=DROP_COLLECTION_TABLE),
        migrations.RunSQL(sql=CREATE_COLLECTIONITEM_TABLE, reverse_sql=DROP_COLLECTIONITEM_TABLE),
    ]




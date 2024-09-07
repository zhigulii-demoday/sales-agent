CREATE TABLE companies (
        id INTEGER DEFAULT nextval('companies_id_seq'::regclass) NOT NULL, 
        name VARCHAR, 
        description TEXT, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        deleted_at TIMESTAMP, 
        CONSTRAINT companies_pkey PRIMARY KEY (id)
)



CREATE TABLE platforms (
        id INTEGER DEFAULT nextval('platforms_id_seq'::regclass) NOT NULL, 
        name VARCHAR, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        deleted_at TIMESTAMP, 
        CONSTRAINT platforms_pkey PRIMARY KEY (id)
)




CREATE TABLE contacts (
        id INTEGER DEFAULT nextval('contacts_id_seq'::regclass) NOT NULL, 
        platform_id INTEGER NOT NULL, 
        platform_uid VARCHAR NOT NULL, 
        send_initial_message TIMESTAMP, 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        deleted_at TIMESTAMP, 
        CONSTRAINT contacts_pkey PRIMARY KEY (id), 
        CONSTRAINT contacts_platform_id_fkey FOREIGN KEY(platform_id) REFERENCES platforms (id)
)



CREATE TABLE reviews (
        id INTEGER DEFAULT nextval('reviews_id_seq'::regclass) NOT NULL, 
        company_id INTEGER NOT NULL, 
        product_cat VARCHAR, 
        product_name VARCHAR, 
        review_dt TIMESTAMP, 
        review_text VARCHAR, 
        topic VARCHAR, 
        sentiment VARCHAR, 
        marketplace VARCHAR, 
        embedding VECTOR(20), 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        deleted_at TIMESTAMP, 
        CONSTRAINT reviews_pkey PRIMARY KEY (id), 
        CONSTRAINT reviews_company_id_fkey FOREIGN KEY(company_id) REFERENCES companies (id)
)

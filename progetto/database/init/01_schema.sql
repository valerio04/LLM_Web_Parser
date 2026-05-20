CREATE DATABASE IF NOT EXISTS minerva_db;

USE minerva_db;

CREATE TABLE IF NOT EXISTS web_resources (
    url VARCHAR(2048) CHARACTER SET ascii PRIMARY KEY,
    domain VARCHAR(255) NOT NULL,
    title TEXT,
    html_text LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold_standard (
    url VARCHAR(2048) CHARACTER SET ascii PRIMARY KEY,
    gold_text LONGTEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_gold_standard_web_resource
        FOREIGN KEY (url)
        REFERENCES web_resources(url)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS parsed_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(2048) CHARACTER SET ascii NOT NULL,
    parsed_text LONGTEXT NOT NULL,
    parser_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_parsed_documents_web_resource
        FOREIGN KEY (url)
        REFERENCES web_resources(url)
        ON DELETE CASCADE,
    UNIQUE KEY unique_parsed_url (url)
);

CREATE TABLE IF NOT EXISTS evaluations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(2048) CHARACTER SET ascii NOT NULL,
    parsed_document_id INT,
    precision_score DOUBLE,
    recall_score DOUBLE,
    f1_score DOUBLE,
    x_eval JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluations_web_resource
        FOREIGN KEY (url)
        REFERENCES web_resources(url)
        ON DELETE CASCADE,
    CONSTRAINT fk_evaluations_parsed_document
        FOREIGN KEY (parsed_document_id)
        REFERENCES parsed_documents(id)
        ON DELETE SET NULL,
    UNIQUE KEY unique_evaluation_url (url)
);

CREATE TABLE IF NOT EXISTS llm_judgements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(2048) CHARACTER SET ascii NOT NULL,
    parsed_document_id INT,
    model_name VARCHAR(255) NOT NULL,
    judge_score DOUBLE,
    judge_feedback TEXT,
    extra_info JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_llm_judgements_web_resource
        FOREIGN KEY (url)
        REFERENCES web_resources(url)
        ON DELETE CASCADE,
    CONSTRAINT fk_llm_judgements_parsed_document
        FOREIGN KEY (parsed_document_id)
        REFERENCES parsed_documents(id)
        ON DELETE SET NULL,
    UNIQUE KEY unique_judgement_url (url)
);
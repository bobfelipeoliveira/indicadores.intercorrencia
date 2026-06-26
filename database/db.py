import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "sgoi.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        operadora TEXT,
        telefone TEXT,
        data_cadastro TEXT,
        status TEXT DEFAULT 'Ativo',
        observacoes TEXT
    );

    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT UNIQUE,
        paciente_id INTEGER,
        paciente_nome TEXT,
        telefone TEXT,
        area TEXT,
        origem TEXT,
        destino TEXT,
        tipo TEXT,
        categoria TEXT,
        subcategoria TEXT,
        descricao TEXT,
        status TEXT DEFAULT 'Aberto',
        prioridade TEXT DEFAULT 'Normal',
        prazo TEXT,
        data_abertura TEXT,
        hora_abertura TEXT,
        responsavel TEXT,
        data_encerramento TEXT,
        observacoes TEXT,
        solicitante TEXT,
        operadora TEXT,
        classificacao TEXT,
        motivo TEXT,
        resposta TEXT,
        horas_consumidas REAL,
        status_prazo TEXT,
        criado_por TEXT DEFAULT 'Intercorrência',
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
    );

    CREATE TABLE IF NOT EXISTS ligacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        call_id TEXT,
        data_hora TEXT,
        telefone_externo TEXT,
        agente_inicial TEXT,
        agente_final TEXT,
        grupo_inicial TEXT,
        grupo_final TEXT,
        total_transferencias INTEGER DEFAULT 0,
        duracao TEXT,
        abandonada INTEGER DEFAULT 0,
        mes TEXT,
        ano INTEGER
    );

    CREATE TABLE IF NOT EXISTS call_back (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_nome TEXT,
        telefone TEXT,
        data_abertura TEXT,
        data_encerramento TEXT,
        dias_aberto INTEGER,
        status TEXT DEFAULT 'Aberto',
        responsavel TEXT,
        observacoes TEXT
    );

    CREATE TABLE IF NOT EXISTS monitoramentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
        paciente_nome TEXT,
        situacao TEXT,
        pendencia TEXT,
        conduta TEXT,
        status TEXT DEFAULT 'Ativo',
        proxima_acao TEXT,
        data_proxima_acao TEXT,
        observacoes TEXT,
        data_registro TEXT,
        responsavel TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
    );

    CREATE TABLE IF NOT EXISTS pendencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_nome TEXT,
        origem TEXT,
        tipo TEXT,
        prioridade TEXT DEFAULT 'Normal',
        prazo TEXT,
        status TEXT DEFAULT 'Aberta',
        responsavel TEXT,
        observacoes TEXT,
        proxima_acao TEXT,
        data_registro TEXT
    );

    CREATE TABLE IF NOT EXISTS indicadores_diarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        mes TEXT,
        ano INTEGER,
        ligacoes_entrantes_crc INTEGER DEFAULT 0,
        ligacoes_transferidas_emerg INTEGER DEFAULT 0,
        perc_atendidas REAL DEFAULT 0,
        tickets_abertos_sem_sucesso INTEGER DEFAULT 0,
        ligacoes_noite INTEGER DEFAULT 0,
        ligacoes_atendidas_noite INTEGER DEFAULT 0,
        perc_atendidas_noite REAL DEFAULT 0,
        ligacoes_entrantes_emerg_dia INTEGER DEFAULT 0,
        ligacoes_atendidas_emerg_dia INTEGER DEFAULT 0,
        perc_atendidas_emerg_dia REAL DEFAULT 0,
        ligacoes_transferidas_emerg_dia INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS consolidado_mensal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mes TEXT,
        ano INTEGER,
        ligacoes_entrantes_grupo INTEGER DEFAULT 0,
        ligacoes_atendidas_grupo INTEGER DEFAULT 0,
        perc_atendida REAL DEFAULT 0,
        tickets_abertos_callback INTEGER DEFAULT 0,
        tickets_fechados_callback INTEGER DEFAULT 0,
        sla_callback REAL DEFAULT 0,
        ligacoes_crc_intercorrencia INTEGER DEFAULT 0,
        ligacoes_atendidas_crc INTEGER DEFAULT 0,
        perc_atendidas_crc REAL DEFAULT 0,
        tickets_abertos INTEGER DEFAULT 0,
        tickets_fechados INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS importacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arquivo TEXT,
        tipo TEXT,
        data_importacao TEXT,
        registros_importados INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Concluído'
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")

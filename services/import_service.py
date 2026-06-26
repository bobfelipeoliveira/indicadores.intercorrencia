import pandas as pd
import sqlite3
import os
import re
from datetime import datetime
from database.db import get_connection, DB_PATH

def parse_duration(dur_str):
    """Convert HH:MM:SS string to total minutes."""
    if pd.isna(dur_str) or str(dur_str).strip() == '':
        return 0
    try:
        parts = str(dur_str).strip().split(':')
        if len(parts) == 3:
            return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 60
        return 0
    except:
        return 0

def import_excel(filepath: str):
    """Main import function for the Solar Cuidados Excel file."""
    conn = get_connection()
    c = conn.cursor()
    results = {}

    xl = pd.read_excel(filepath, sheet_name=None, header=None)

    # --- PACIENTES DE MAIO ---
    if 'PACIENTES DE MAIO' in xl:
        df = xl['PACIENTES DE MAIO'].copy()
        df.columns = ['nome', 'tickets_abertos']
        df = df[df['nome'].notna() & (df['nome'] != 'PACIENTE')]
        count = 0
        for _, row in df.iterrows():
            existing = c.execute("SELECT id FROM pacientes WHERE nome=?", (row['nome'],)).fetchone()
            if not existing:
                c.execute("INSERT INTO pacientes (nome, data_cadastro, status) VALUES (?,?,?)",
                          (str(row['nome']).strip(), '2026-05-01', 'Ativo'))
                count += 1
        results['pacientes'] = count

    # --- TICKETS MAIO ---
    for sheet_key, mes, ano, criado_por in [
        ('Tickets - MAIO', '2026-05', 2026, 'Intercorrência'),
        ('Tickets - JUN', '2026-06', 2026, 'Intercorrência'),
    ]:
        if sheet_key not in xl:
            continue
        raw = xl[sheet_key]
        header_row = None
        for i, row in raw.iterrows():
            vals = [str(v).strip().upper() for v in row.values if str(v).strip()]
            if any(k in vals for k in ['SOLICITANTE', 'TICKET', 'PACIENTE']):
                header_row = i
                break
        if header_row is None:
            continue
        df = xl[sheet_key].iloc[header_row:].copy()
        df.columns = [str(c).strip() for c in df.iloc[0].values]
        df = df.iloc[1:].reset_index(drop=True)

        # Normalize column names for both sheets
        col_map = {}
        for col in df.columns:
            col_upper = col.upper()
            if 'SOLICITANTE' in col_upper:
                col_map[col] = 'solicitante'
            elif col_upper in ['DATA A', 'DATA SOLICITAÇÃO']:
                col_map[col] = 'data_abertura'
            elif col_upper in ['DATA F', 'DATA ENCERRAMENTO']:
                col_map[col] = 'data_encerramento'
            elif col_upper in ['HR C', 'HORAS CONSUMIDAS']:
                col_map[col] = 'horas_consumidas'
            elif col_upper in ['TC', 'TICKET', 'TICKET SOLICITACAO']:
                col_map[col] = 'numero'
            elif 'PACIENTE' in col_upper:
                col_map[col] = 'paciente_nome'
            elif col_upper in ['OPS', 'OPERADORA']:
                col_map[col] = 'operadora'
            elif col_upper in ['EQUIPE EXECUTORA', 'GRUPO RESPONSÁVEL']:
                col_map[col] = 'area'
            elif 'MANIFESTAÇÃO' in col_upper or 'TIPO SOLICITAÇÃO' in col_upper or col_upper == 'TIPO':
                col_map[col] = 'classificacao'
            elif col_upper == 'ORIGEM':
                col_map[col] = 'origem'
            elif col_upper in ['MOTIVO', 'MOTIVO']:
                col_map[col] = 'motivo'
            elif 'DESCRIÇÃO' in col_upper or 'DESCRICAO' in col_upper:
                col_map[col] = 'descricao'
            elif col_upper in ['CLASS', 'CLASSIFICAÇÃO']:
                col_map[col] = 'categoria'
            elif col_upper in ['RESPOSTA', 'RESPOSTA SOLICITAÇÃO']:
                col_map[col] = 'resposta'
            elif col_upper == 'STATUS':
                col_map[col] = 'status'
            elif 'STATUS PRAZO' in col_upper:
                col_map[col] = 'status_prazo'
            elif 'STATUS TICKET' in col_upper:
                col_map[col] = 'status_ticket'

        df = df.rename(columns=col_map)
        count = 0
        for _, row in df.iterrows():
            num = str(row.get('numero', '')).strip()
            if not num or num.upper() in ['TC', 'TICKET', 'TICKET SOLICITACAO', 'NAN']:
                continue
            existing = c.execute("SELECT id FROM tickets WHERE numero=?", (num,)).fetchone()
            if existing:
                continue

            pac = str(row.get('paciente_nome', '')).strip()
            pac_id = None
            if pac and pac.lower() != 'nan':
                p = c.execute("SELECT id FROM pacientes WHERE nome=?", (pac,)).fetchone()
                if p:
                    pac_id = p['id']
                else:
                    c.execute("INSERT INTO pacientes (nome, data_cadastro, status) VALUES (?,?,?)",
                              (pac, '2026-01-01', 'Ativo'))
                    pac_id = c.lastrowid

            def safe(key, default=''):
                v = row.get(key, default)
                return str(v).strip() if not pd.isna(v) else default

            data_ab = safe('data_abertura')
            try:
                data_ab = pd.to_datetime(data_ab).strftime('%Y-%m-%d') if data_ab else ''
            except:
                data_ab = ''

            data_enc = safe('data_encerramento')
            try:
                data_enc = pd.to_datetime(data_enc).strftime('%Y-%m-%d') if data_enc else ''
            except:
                data_enc = ''

            hrs = row.get('horas_consumidas', 0)
            try:
                hrs = float(hrs) if not pd.isna(hrs) else 0
            except:
                hrs = 0

            status_val = safe('status', 'Fechado') if data_enc else 'Aberto'
            if 'aprovado' in safe('status_ticket', '').lower():
                status_val = 'Fechado'

            classificacao = safe('classificacao')
            tipo_ticket = 'Solicitação'
            if 'INFORMAÇÃO' in classificacao.upper():
                tipo_ticket = 'Informação'
            elif 'MANIFESTA' in classificacao.upper():
                tipo_ticket = 'Manifestação'

            c.execute("""
                INSERT INTO tickets (numero, paciente_id, paciente_nome, area, origem, tipo, classificacao,
                    motivo, descricao, categoria, resposta, solicitante, operadora,
                    data_abertura, data_encerramento, horas_consumidas, status, status_prazo, criado_por)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (num, pac_id, pac, safe('area'), safe('origem'), tipo_ticket,
                  classificacao, safe('motivo'), safe('descricao'),
                  safe('categoria'), safe('resposta'), safe('solicitante'),
                  safe('operadora'), data_ab, data_enc, hrs, status_val,
                  safe('status_prazo'), criado_por))
            count += 1
        results[f'tickets_{sheet_key}'] = count

    # --- LIGAÇÕES TRANSFERIDAS ---
    for sheet_key, mes in [('Ligações Transferidas MAIO', '2026-05'), ('LIGAÇÕES TRANSFERIDAS - JUN', '2026-06')]:
        if sheet_key not in xl:
            continue
        raw = xl[sheet_key]
        header_row = None
        for i, row in raw.iterrows():
            vals = [str(v).strip() for v in row.values]
            if 'Call' in vals and 'Hora de início' in vals:
                header_row = i
                break
        if header_row is None:
            continue
        df = xl[sheet_key].iloc[header_row:].copy()
        df.columns = [str(v).strip() for v in df.iloc[0].values]
        df = df.iloc[1:].reset_index(drop=True)
        count = 0
        ano = int(mes[:4])
        for _, row in df.iterrows():
            call_id = str(row.get('Call', '')).strip()
            if not call_id or 'Call ID' not in call_id:
                continue
            call_id_clean = call_id.replace('Call ID:', '').strip()
            existing = c.execute("SELECT id FROM ligacoes WHERE call_id=?", (call_id_clean,)).fetchone()
            if existing:
                continue
            data_hora = str(row.get('Hora de início', '')).strip()
            try:
                data_hora = pd.to_datetime(data_hora).strftime('%Y-%m-%d %H:%M:%S')
            except:
                data_hora = ''
            abandonada = 1 if str(row.get('Is Abandoned', 'FALSE')).strip().upper() == 'TRUE' else 0
            dur = str(row.get('Duração da Ligação', '')).strip()
            transfers = row.get('Total Times Transferred', 0)
            try:
                transfers = int(float(transfers)) if not pd.isna(transfers) else 0
            except:
                transfers = 0
            c.execute("""
                INSERT INTO ligacoes (call_id, data_hora, telefone_externo, agente_inicial, agente_final,
                    grupo_inicial, grupo_final, total_transferencias, duracao, abandonada, mes, ano)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (call_id_clean, data_hora,
                  str(row.get('Parte Externa', '')).strip(),
                  str(row.get('Agente Inicial', '')).strip(),
                  str(row.get('Agente final', '')).strip(),
                  str(row.get('Grupo inicial', '')).strip(),
                  str(row.get('Grupo Final', '')).strip(),
                  transfers, dur, abandonada, mes, ano))
            count += 1
        results[f'ligacoes_{sheet_key}'] = count

    # --- INDICADORES DIARIOS MAIO ---
    for sheet_key, mes, ano in [('INDICADORES - MAIO', '2026-05', 2026), ('INDICADORES - JUN', '2026-06', 2026)]:
        if sheet_key not in xl:
            continue
        raw = xl[sheet_key]
        df = raw.copy()
        df = df.dropna(how='all').reset_index(drop=True)
        # First col = metric name, rest = daily values
        # Find header row with dates
        header_row = 0
        df_t = df.set_index(df.columns[0]).T
        df_t.index = pd.to_datetime(df_t.index, errors='coerce')
        df_t = df_t.dropna()

        row_map = {}
        for col in df.iloc[:, 0]:
            col_str = str(col).strip().upper()
            if 'LIGAÇÕES ENTRANTES CRC' in col_str:
                row_map['ligacoes_entrantes_crc'] = col
            elif 'LIGAÇÕES TRANSFERIDAS EMERGÊNCIA' in col_str and 'DIA' not in col_str:
                row_map['ligacoes_transferidas_emerg'] = col
            elif '% ATENDIDA' in col_str:
                row_map['perc_atendidas'] = col
            elif 'SEM SUCESSO' in col_str:
                row_map['tickets_abertos_sem_sucesso'] = col
            elif 'NOITE' in col_str and 'ENTRANTES' in col_str:
                row_map['ligacoes_noite'] = col
            elif 'ENTRANTES EMERGÊNCIA DIA' in col_str:
                row_map['ligacoes_entrantes_emerg_dia'] = col
            elif 'ATENDIDAS EMERGÊNCIA DIA' in col_str:
                row_map['ligacoes_atendidas_emerg_dia'] = col

        count = 0
        for date_idx, row_data in df_t.iterrows():
            if pd.isna(date_idx):
                continue
            data_str = date_idx.strftime('%Y-%m-%d')
            existing = c.execute("SELECT id FROM indicadores_diarios WHERE data=?", (data_str,)).fetchone()
            if existing:
                continue

            def gval(key):
                col_name = row_map.get(key)
                if col_name is None:
                    return 0
                v = row_data.get(col_name, 0)
                try:
                    return float(v) if not pd.isna(v) else 0
                except:
                    return 0

            c.execute("""
                INSERT INTO indicadores_diarios (data, mes, ano, ligacoes_entrantes_crc,
                    ligacoes_transferidas_emerg, perc_atendidas, tickets_abertos_sem_sucesso,
                    ligacoes_noite, ligacoes_entrantes_emerg_dia, ligacoes_atendidas_emerg_dia)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (data_str, mes, ano, gval('ligacoes_entrantes_crc'),
                  gval('ligacoes_transferidas_emerg'), gval('perc_atendidas'),
                  gval('tickets_abertos_sem_sucesso'), gval('ligacoes_noite'),
                  gval('ligacoes_entrantes_emerg_dia'), gval('ligacoes_atendidas_emerg_dia')))
            count += 1
        results[f'indicadores_{sheet_key}'] = count

    # --- CONSOLIDADO ---
    if 'CONSOLIDADO-MAIO' in xl:
        raw = xl['CONSOLIDADO-MAIO']
        rows = {}
        for _, row in raw.iterrows():
            k = str(row.iloc[0]).strip().upper()
            v = row.iloc[1]
            try:
                v = float(v)
            except:
                v = 0
            rows[k] = v
            if not pd.isna(row.iloc[4]):
                k2 = str(row.iloc[4]).strip().upper()
                v2 = row.iloc[5]
                try:
                    v2 = float(v2)
                except:
                    v2 = 0
                rows[k2] = v2

        existing = c.execute("SELECT id FROM consolidado_mensal WHERE mes=? AND ano=?", ('2026-05', 2026)).fetchone()
        if not existing:
            c.execute("""
                INSERT INTO consolidado_mensal (mes, ano, ligacoes_entrantes_grupo, ligacoes_atendidas_grupo,
                    perc_atendida, tickets_abertos_callback, tickets_fechados_callback, sla_callback,
                    ligacoes_crc_intercorrencia)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, ('2026-05', 2026,
                  rows.get('LIGAÇÕES ENTRANTES GRUPO', 0),
                  rows.get('LIGAÇÕES ATENDIDAS GRUPO', 0),
                  rows.get('% ATENDIDA', 0),
                  rows.get('TICKETS ABERTOS CALL BACK', 0),
                  rows.get('TICKETS FECHADOS CALL BACK', 0),
                  rows.get('SLA CALL BACK', 0),
                  rows.get('LIGAÇÕES ENTRANTES CRC PARA INTERCORRÊNCIA', 0)))
            results['consolidado'] = 1

    conn.commit()
    conn.close()
    return results

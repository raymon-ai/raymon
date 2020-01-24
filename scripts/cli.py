import psycopg2
import json
import fire
import yaml


ORCH_INSERT = """INSERT INTO orchestration(project_id, cfg)
VALUES (%s,  %s)
ON CONFLICT(project_id) DO UPDATE SET cfg = EXCLUDED.cfg;
"""

def apply_orchestration(project_id, fpath):
    conn = psycopg2.connect(host="localhost", port=5432, dbname='raymon', user='postgres', password='crayray')
    cfg = {}
    with open(fpath, 'r') as fp:
        cfg = json.dumps(yaml.full_load(fp), indent=4)
    print(f"Project: {project_id} ({type(project_id)})")
    print(f"Cfg: \n{cfg}")

    cur = conn.cursor()
    cur.execute(ORCH_INSERT, (project_id, cfg))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted new orchestration for project {project_id}")


if __name__ == '__main__':
  fire.Fire()

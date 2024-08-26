from aiohttp import web
from server import PromptServer
import sqlite3
import os
# from aiohttp import web
routes = PromptServer.instance.routes
current_path = os.path.abspath(os.path.dirname(__file__))


assets_dir = os.path.join(current_path, "web/assets")
print(f"assets_dir:{assets_dir}")
PromptServer.instance.app.router.add_static(
    "/art.quanse/web/assets/", path=assets_dir
)

@routes.post('/art.quanse/cp/add')
async def my_function(request):
    data = await request.json()
    name = data.get('name')
    version = data.get('version')
    url = data.get('url')
    vae = data.get('vae')
    clip_skip = data.get('clip_skip')
    description = data.get('description')
    info = CheckPointInfo()
    info.add_checkpoint_data(name, version, url, vae, clip_skip, description)
    return web.json_response({"msg":"ok"})


@routes.put('/art.quanse/cp/update')
async def my_function(request):
    data = await request.json()
    id =int(data.get('id'))
    name = data.get('name')
    version = data.get('version')
    url = data.get('url')
    vae = bool(data.get('vae'))
    print(f"vae:{vae}")
    clip_skip = data.get('clip_skip')
    description = data.get('description')
    CheckPointInfo.update_checkpoint_data(id,name, version, url, vae, clip_skip, description)
    return web.json_response({"msg":"update ok"})


@routes.get('/art.quanse/cp/info/{name}')
async def my_function(request):
    name = request.match_info['name']
    info = CheckPointInfo()
    return web.json_response(info.get_checkpoint_data(name))

@routes.delete('/art.quanse/cp/delete/{id}')
async def my_function(request):
    id = int(request.match_info['id'])
    info = CheckPointInfo()
    info.delete_checkpoint(id)
    return web.json_response({"msg":"ok"})

@routes.get('/art.quanse/cp/page')
async def page(request):
     page = request.query.get('page',1)
     page = int(page)
     info = CheckPointInfo()
     return web.json_response(info.get_paginated_checkpoints(page))


@routes.get('/art.quanse/web')
async def mixlab_app_handler(request):
    html_file = os.path.join(current_path, "web/index.html")
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            html_data = f.read()
            return web.Response(text=html_data, content_type='text/html')
    else:
        return web.Response(text="HTML file not found", status=404)


class CheckPointInfo:
    db_file = 'comfy_ui_checkpoints.db'
   
    def __init__(self):
        pass

    @classmethod
    def get_checkpoint_data(self,name):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("SELECT * FROM checkpoints WHERE name=?", (name,))
        data = c.fetchone()
        conn.close()
        return data
    
    @classmethod
    def delete_checkpoint(self,id):
        try:
            print(f"delete{id}")
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute("SELECT * FROM checkpoints WHERE id=?", (id,))
            existing_data = c.fetchone()
            print(f"existing_data:{existing_data}")
            c.execute("DELETE FROM checkpoints WHERE id=?", (id,))
            data=c.fetchone()
            conn.commit()
            print(f"data:{data}")
            conn.close()
        except sqlite3.Error as e:
            print(f"Error deleting checkpoint: {e}")
    
    @classmethod
    def add_checkpoint_data(self,name, version, url, vae, clip_skip,description):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("INSERT INTO checkpoints (name, version, url, vae, clip_skip,description) VALUES (?,?,?,?,?,?)",
                    (name, version, url, vae, clip_skip,description))
        conn.commit()
        conn.close()

    @classmethod
    def check_table(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        # 检查表是否存在
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints';")
        table_exists = c.fetchone() is not None

        # 如果表不存在，则创建表
        if not table_exists:
            c.execute('''CREATE TABLE checkpoints
                        (id INTEGER PRIMARY KEY, name TEXT, version TEXT, url TEXT, vae BOOLEAN, clip_skip INTEGER,description TEXT)''')
        conn.commit()
        conn.close()

    @classmethod
    def update_checkpoint_data(self, id, name, version, url, vae_value, clip_skip_value, description):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("UPDATE checkpoints SET name=?, version=?, url=?, vae=?, clip_skip=?, description=? WHERE id=?",
                  (name, version, url, vae_value, clip_skip_value, description, id,))
        conn.commit()
        conn.close()

    @classmethod
    def get_paginated_checkpoints(cls, page, per_page=10):
        try:
            page = int(page)
            if page < 1:
                raise ValueError("Page must be a positive integer.")
            offset = (page - 1) * per_page
            query = """
            SELECT id, name, version, url, vae, clip_skip, description
            FROM checkpoints
            LIMIT? OFFSET?
            """
            countQuery = """
            SELECT count(*)
            FROM checkpoints
            """
            conn = sqlite3.connect(cls.db_file)
            c = conn.cursor()
            c.execute(query, (per_page, offset))
            rows = c.fetchall()
            c.execute(countQuery)
            total_count = c.fetchone()[0]
            conn.commit()
            conn.close()
            checkpoints = []
            for row in rows:
                checkpoints.append({
                    'id': row[0],
                    'name': row[1],
                    'version': row[2],
                    'url': row[3],
                    'vae': bool(row[4]),
                    'clip_skip': row[5],
                    'description': row[6]
                })
            return {'checkpoints': checkpoints, 'total_count': total_count}
        except (ValueError, sqlite3.Error) as e:
            print(f"Error: {e}")
            return [], 0
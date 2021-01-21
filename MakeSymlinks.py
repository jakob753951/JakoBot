import os

from_dir = 'available_cogs'
to_dir = 'enabled_cogs'
for file_name in [name for name in os.listdir(to_dir) if os.path.isfile(f'{to_dir}/{name}')]:
    from_path = f'{from_dir}/{file_name}'
    to_path = f'{to_dir}/{file_name}'
    if os.path.exists(to_path):
        os.remove(to_path)
    os.link(from_path, to_path)
import click
import subprocess
import json
import os
import requests
import json
import os
import sys
import yaml
from collections import OrderedDict

# Fungsi untuk menjalankan perintah shell dan menampilkan output secara real-time
def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        sys.stdout.write(line.decode())
    process.stdout.close()
    process.wait()
    return process.returncode


@click.command()
@click.option('--project', prompt='Output project', help='Menambahkan project.')
@click.option('--port', prompt='Output port', help='Menambahkan port.')
@click.option('--chart_repo', prompt='Output chart_repo', help='Menambahkan chartrepo.')
@click.option('--chart_name', prompt='Output chart_name', help='Menambahkan chartname.')
def jsonv1(project, nodetype, port, chart_repo, chart_name):
    """
    CLI untuk membuat file init.json di current directory yang berisi nama repository
    dan commit hash terakhir dari Git.
    """
    try:
        # Mengambil nama repository dengan git CLI
        repo_name = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.STDOUT
        ).decode('utf-8').strip().split('/')[-1]

        # Membuat folder helminit jika belum ada
        devops_folder = os.path.join(os.getcwd(), 'devops')
        os.makedirs(devops_folder, exist_ok=True)

        # Membuat dictionary dengan data yang akan disimpan ke file JSON
        data = {
            "repo_name": repo_name,
            "image_name": repo_name,
            "project": project,
            "port": port,
            "chart_repo": chart_repo,
            "chart_name": chart_name
        }

        # Menentukan lokasi output file di current directory (init.json)
        output_path = os.path.join(devops_folder, 'init.json')

        # Menyimpan data ke file JSON di current directory
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        click.echo(f"File init.json berhasil dibuat di: {output_path} dengan isi: {data}")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error saat menjalankan perintah git: {e.output.decode('utf-8')}")
    except Exception as e:
        click.echo(f"Terjadi kesalahan: {e}")



@click.command()
@click.option('--project', prompt='Output project', help='Menambahkan project.')
@click.option('--port1', prompt='Output port1', help='Menambahkan port1.')
@click.option('--port2', prompt='Output port2', help='Menambahkan port2.')
@click.option('--chart_repo', prompt='Output chart_repo', help='Menambahkan chartrepo.')
@click.option('--chart_name', prompt='Output chart_name', help='Menambahkan chartname.')
def jsonv2(project, nodetype, port1, port2, chart_repo, chart_name):
    """
    CLI untuk membuat file init.json di current directory yang berisi nama repository
    dan commit hash terakhir dari Git.
    """
    try:
        # Mengambil nama repository dengan git CLI
        repo_name = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'], stderr=subprocess.STDOUT
        ).decode('utf-8').strip().split('/')[-1]

        # Membuat folder helminit jika belum ada
        devops_folder = os.path.join(os.getcwd(), 'devops')
        os.makedirs(devops_folder, exist_ok=True)

        # Membuat dictionary dengan data yang akan disimpan ke file JSON
        data = {
            "repo_name": repo_name,
            "image_name": repo_name,
            "project": project,
            "port1": port1,
            "port2": port2,
            "chart_repo": chart_repo,
            "chart_name": chart_name
        }

        # Menentukan lokasi output file di current directory (init.json)
        output_path = os.path.join(devops_folder, 'init.json')

        # Menyimpan data ke file JSON di current directory
        with open(output_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        click.echo(f"File init.json berhasil dibuat di: {output_path} dengan isi: {data}")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error saat menjalankan perintah git: {e.output.decode('utf-8')}")
    except Exception as e:
        click.echo(f"Terjadi kesalahan: {e}")


@click.command()
@click.option('--env', prompt='Output env', help='Menambahkan chart.')
def getval(env):
    """
    Get values from helmchart
    """
    # Tentukan path ke folder dan file output
    values_folder = os.path.join(os.getcwd(), 'devops', 'values')
    os.makedirs(values_folder, exist_ok=True)  # Buat folder jika belum ada
    output_file_path = os.path.join(values_folder, f'{env}-values.yaml')
    
    # Tentukan path ke file init.json
    init_file_path = os.path.join(os.getcwd(), 'devops', 'init.json')
    
    try:
        # Membaca dan mem-parsing file JSON
        with open(init_file_path, 'r') as json_file:
            data = json.load(json_file, object_pairs_hook=OrderedDict)

        # Mengambil nilai dari nama_repo dan commitid
        chart_name = data.get('chart_name')
        chart_repo = data.get('chart_repo')

        # Menjalankan perintah 'helm show values'
        subprocess.run(['helm', 'repo', 'update'], check=True)
        result = subprocess.run(['helm', 'show', 'values', f'{chart_repo}/{chart_name}'], check=True, capture_output=True, text=True)

        
        # Menyimpan output ke file branch-values.yaml
        with open(output_file_path, 'w') as file:
            file.write(result.stdout)

        click.echo(f"Values dari chart '{chart_name}' berhasil disimpan di: {output_file_path}")

    except FileNotFoundError:
        click.echo("File init.json tidak ditemukan di folder devops.", err=True)
    except json.JSONDecodeError:
        click.echo("Error saat mem-parsing file JSON.", err=True)
    except Exception as e:
        click.echo(f"Terjadi kesalahan: {e}", err=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error saat menjalankan perintah helm: {e.stderr}", err=True)
    except Exception as e:
        click.echo(f"Terjadi kesalahan: {e}", err=True)


@click.command()
@click.option('--env', prompt='Output env', help='Menambahkan chart.')
def setval(env):
    """
    CLI untuk mengubah nilai dalam file values.yaml dengan nilai dari init.json.
    """
    # Tentukan path ke file init.json
    init_file_path = os.path.join(os.getcwd(), 'devops', 'init.json')

    values_folder = os.path.join(os.getcwd(), 'devops', 'values')
    values_file_path = os.path.join(values_folder, f'{env}-values.yaml')


    # Mengambil commit hash terakhir dengan git CLI
    commit_hash = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT
    ).decode('utf-8').strip()
    
    try:
        # Membaca dan mem-parsing file JSON
        with open(init_file_path, 'r') as json_file:
            json_data = json.load(json_file)

        # Mengambil nilai dari nama_repo dan commitid
        repo_name = json_data.get('repo_name')
        image_name = json_data.get('image_name')
        project = json_data.get('project')
        nodetype = json_data.get('nodetype')
        chart_name = json_data.get('chart_name')
        secret_name= f'file-config-{repo_name}'
        volume_name= f'file-config-{repo_name}-secret-volume'
        read_only = True

        # Membaca dan mem-parsing file values.yaml
        with open(values_file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file) or OrderedDict()
        
        # Mengubah nilai dalam values.yaml berdasarkan nilai dari init.json
        # Misalnya, ganti key tertentu sesuai dengan data dari JSON
        # yaml_data['image.reposistory'] = json_data.get('repo_name', yaml_data.get('image.reposistory'))
        yaml_data['image']['repository'] =  image_name # Mengubah nilai jika key ada
        yaml_data['image']['tag'] =  commit_hash # Mengubah nilai jika key ada
        yaml_data['appLabels']['app'] =  repo_name # Mengubah nilai jika key ada
        yaml_data['appLabels']['project'] =  project # Mengubah nilai jika key ada
        yaml_data['appLabels']['role'] =  nodetype # Mengubah nilai jika key ada
        yaml_data['appLabels']['env'] =  env # Mengubah nilai jika key ada

        yaml_data['nodeSelector']['nodetype'] =  nodetype # Mengubah nilai jika key ada

        if chart_name == 'chartgo':
            port = json_data.get('port')
            yaml_data['service']['port'] =  port # Mengubah nilai jika key ada
        elif chart_name == 'chartgov2':
            port1 = json_data.get('port1')
            port2 = json_data.get('port2')
            yaml_data['service']['port'] =  port1 # Mengubah nilai jika key ada
            yaml_data['grpcService']['port'] =  port2 # Mengubah nilai jika key ada

        # Menyimpan kembali data yang telah diubah ke dalam file values.yaml
        with open(values_file_path, 'w') as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False)


    except FileNotFoundError as e:
        click.echo(f"File tidak ditemukan: {e}", err=True)
    except json.JSONDecodeError:
        click.echo("Error saat mem-parsing file JSON.", err=True)
    except yaml.YAMLError:
        click.echo("Error saat mem-parsing file YAML.", err=True)
    except Exception as e:
        click.echo(f"Terjadi kesalahan: {e}", err=True)





@click.group()
def cli():
    pass

cli.add_command(jsonv1)
cli.add_command(jsonv2)
cli.add_command(getval)
cli.add_command(setval)

if __name__ == '__main__':
    cli()
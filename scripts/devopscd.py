import os
import click
import subprocess
import sys
import json

# Fungsi untuk menjalankan perintah shell dan menampilkan output secara real-time
def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        sys.stdout.write(line.decode())
    process.stdout.close()
    process.wait()
    return process.returncode



@click.command()
@click.option('--env', prompt='Output env', help='Menambahkan chart.')
def deploy(env):
    """
    Helm Deploy Install Or Upgrade
    """

    # Tentukan path ke file init.json
    init_file_path = os.path.join(os.getcwd(), 'devops', 'init.json')

    # Membaca dan mem-parsing file JSON
    with open(init_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Mengambil nilai dari nama_repo dan commitid
    repo_name = json_data.get('repo_name')
    project = json_data.get('project')
    chart_repo = json_data.get('chart_repo')
    chart_name = json_data.get('chart_name')
    chart = f"{chart_repo}/{chart_name}"
    namespace= f"{env}-{project}"

    
    # Periksa apakah Dockerfile ada
    values = os.path.join(os.getcwd(), 'devops', 'values', f"{env}-values.yaml")
    if not os.path.exists(values):
        click.echo(f"Error: values '{values}' tidak ditemukan.")
        sys.exit(1)

    subprocess.run(['helm', 'repo', 'update'], check=True)
    try:
        # Periksa apakah release sudah ada dengan helm list
        check_release_command = [
            "helm", "list", "-n", namespace, "--filter", repo_name, "-q"
        ]
        result = subprocess.run(check_release_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        release_exists = result.stdout.strip()

        if release_exists:
            click.echo(f"Release '{repo_name}' sudah ada. Melakukan helm upgrade...")
            
            # Jika release sudah ada, lakukan upgrade
            upgrade_command = ["helm", "upgrade", repo_name, chart, "-n", namespace]
            if values:
                upgrade_command += ["-f", values]
            subprocess.run(upgrade_command, check=True)
            click.echo(f"Helm release '{repo_name}' berhasil diupgrade.")

        else:
            click.echo(f"Release '{repo_name}' belum ada. Melakukan helm install...")

            # Jika release belum ada, lakukan install
            install_command = ["helm", "install", repo_name, chart, "-n", namespace]
            if values:
                install_command += ["-f", values]
            subprocess.run(install_command, check=True)
            click.echo(f"Helm release '{repo_name}' berhasil diinstall.")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error saat menjalankan Helm command: {e}", err=True)
    except Exception as e:
        click.echo(f"Terjadi kesalahan: {e}", err=True)

@click.command()
@click.option('--env', prompt='Output env', help='Menambahkan chart.')
def uninstall(env):
    """
    Helm Uninstall Release
    """

    # Tentukan path ke file init.json
    init_file_path = os.path.join(os.getcwd(), 'devops', 'init.json')

    # Membaca dan mem-parsing file JSON
    with open(init_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Mengambil nilai dari nama_repo dan commitid
    repo_name = json_data.get('repo_name')
    project = json_data.get('project')
    namespace= f"{env}-{project}"


    try:
        # Periksa apakah release sudah ada dengan helm list
        check_release_command = [
            "helm", "list", "-n", namespace, "--filter", repo_name, "-q"
        ]
        result = subprocess.run(check_release_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        release_exists = result.stdout.strip()

        if release_exists:
            click.echo(f"Release '{repo_name}' sudah ada. Melakukan helm upgrade...")
            
            # Jika release sudah ada, lakukan upgrade
            upgrade_command = ["helm", "uninstall", repo_name, "-n", namespace]
            subprocess.run(upgrade_command, check=True)
            click.echo(f"Helm release '{repo_name}' berhasil di uninstall.")

        else:
            click.echo(f"Release '{repo_name}' belum ada. Lakukan helm install...")


    except subprocess.CalledProcessError as e:
        click.echo(f"Error saat menjalankan Helm command: {e}", err=True)
    except Exception as e:
        click.echo(f"Terjadi kesalahan: {e}", err=True)
 

@click.group()
def cli():
    """Script CLI untuk build dan release Docker image"""
    pass

cli.add_command(deploy)
cli.add_command(uninstall)

if __name__ == '__main__':
    cli()
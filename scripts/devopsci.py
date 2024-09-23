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
def build():
    """
    Build Docker image dengan tag tertentu
    """

    # Tentukan path ke file init.json
    init_file_path = os.path.join(os.getcwd(), 'devops', 'init.json')

    # Membaca dan mem-parsing file JSON
    with open(init_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Mengambil nilai dari nama_repo dan commitid
    image_name = json_data.get('image_name')
    project = json_data.get('project')


    # Mengambil commit hash terakhir dengan git CLI
    commit_hash = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT
    ).decode('utf-8').strip()
    full_image_name = f"{project}/{image_name}:{commit_hash}"
    
    # Periksa apakah Dockerfile ada
    dockerfile = os.path.join(os.getcwd(), 'Dockerfile')
    if not os.path.exists(dockerfile):
        click.echo(f"Error: Dockerfile '{dockerfile}' tidak ditemukan.")
        sys.exit(1)
   
    try:
        # Memeriksa apakah image sudah ada di local
        result = subprocess.run(
            ["docker", "images", "-q", full_image_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        image_id = result.stdout.strip()

        if image_id:
            click.echo(f"Image {full_image_name} sudah ada di local dengan ID {image_id}.")
        else:
            click.echo(f"Image {full_image_name} tidak ditemukan di local. Mencoba pull dari registry...")

        # Mencoba pull image dari Docker registry
        pull_command = ["docker", "pull", full_image_name]
        pull_result = subprocess.run(pull_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if pull_result.returncode == 0:
            click.echo(f"Image {full_image_name} berhasil dipull dari registry.")
        else:
            click.echo(f"Image {full_image_name} tidak ditemukan di registry. Mulai build...")

                # Memulai proses build Docker
            build_command = [
                    "docker", "build", "-t", full_image_name, "-f", dockerfile, '.'
            ]
            
            subprocess.run(build_command, check=True)
            click.echo(f"Image {full_image_name} berhasil dibangun.")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error saat menjalankan Docker command: {e}", err=True)
    except Exception as e:
        click.echo(f"Terjadi kesalahan: {e}", err=True)

@click.command()
def release():
    """
    Release Docker image ke Docker registry (push)
    """
        # Tentukan path ke file init.json
    init_file_path = os.path.join(os.getcwd(), 'devops', 'init.json')

    # Membaca dan mem-parsing file JSON
    with open(init_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Mengambil nilai dari nama_repo dan commitid
    image_name = json_data.get('image_name')
    project = json_data.get('project')


    # Mengambil commit hash terakhir dengan git CLI
    commit_hash = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT
    ).decode('utf-8').strip()

    full_image_name = f"{project}/{image_name}:{commit_hash}"
    
    # Perintah untuk push Docker image
    push_command = f"docker push {full_image_name}"
    
    click.echo(f"Melakukan push Docker image: {full_image_name}")
    
    if run_command(push_command) != 0:
        click.echo("Error: Gagal push Docker image ke registry.")
        sys.exit(1)
    

    click.echo(f"Berhasil push Docker image: {full_image_name}")


@click.command()
@click.option('--version', prompt='Version tag (e.g., 1.0.0)', help='Tag untuk versi Docker image.')
def tag(version):
    """
    Release Docker image ke Docker registry (push)
    """
        # Tentukan path ke file init.json
    init_file_path = os.path.join(os.getcwd(), 'devops', 'init.json')

    # Membaca dan mem-parsing file JSON
    with open(init_file_path, 'r') as json_file:
        json_data = json.load(json_file)

    # Mengambil nilai dari nama_repo dan commitid
    image_name = json_data.get('image_name')
    project = json_data.get('project')


    # Mengambil commit hash terakhir dengan git CLI
    commit_hash = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT
    ).decode('utf-8').strip()

    full_image_name = f"{project}/{image_name}:{commit_hash}"
    full_image_tag = f"{project}/{image_name}:{version}"

    # Memeriksa apakah image sudah ada di local
    result = subprocess.run(
        ["docker", "images", "-q", full_image_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    image_id = result.stdout.strip()

    if image_id:
        click.echo(f"Image {full_image_name} sudah ada di local dengan ID {image_id}.")
    else:
        click.echo(f"Image {full_image_name} tidak ditemukan di local. Mencoba pull dari registry...")

    # Mencoba pull image dari Docker registry
    pull_command = ["docker", "pull", full_image_name]
    pull_result = subprocess.run(pull_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if pull_result.returncode == 0:
        click.echo(f"Image {full_image_name} berhasil dipull dari registry.")
            
        #TAG IMAGE
        tag_command = f"docker tag {full_image_name} {full_image_tag}"

        click.echo(f"Melakukan TAG Docker image: {full_image_name}")
        
        if run_command(tag_command) != 0:
            click.echo("Error: Gagal push Docker image ke registry.")
            sys.exit(1)

        #PUSH TAG
        push_command = f"docker push {full_image_tag}"
        click.echo(f"Melakukan push Docker image: {full_image_name}")
        
        if run_command(push_command) != 0:
            click.echo("Error: Gagal push Docker image ke registry.")
            sys.exit(1)
        click.echo(f"Berhasil push Docker image: {full_image_name}")
    else:
        click.echo(f"Image {full_image_name} tidak ditemukan di registry, Please build and deploy on DEVELOP. ")
 

@click.group()
def cli():
    """Script CLI untuk build dan release Docker image"""
    pass

cli.add_command(build)
cli.add_command(release)
cli.add_command(tag)

if __name__ == '__main__':
    cli()
import os
import time
import csv
import subprocess
import hashlib
import sys

file_sizes = {
    "10MB": 10 * 1024 * 1024,
    "100MB": 100 * 1024 * 1024,
    "500MB": 500 * 1024 * 1024,
    "1GB": 1 * 1024 * 1024 * 1024,
}


test_dir = "D:\\Temp\\"
os.makedirs(test_dir, exist_ok=True)

csv_file = "benchmark_results.csv"

UPLOAD_COMMAND = "upload {filename}"
DOWNLOAD_COMMAND = "download {filename}"

def generate_file(file_path, size_bytes):
    if os.path.exists(file_path):
        print(f"Arquivo já existe, pulando: {file_path}")
        return
    print(f"Gerando arquivo: {file_path} ({size_bytes} bytes)")
    with open(file_path, "wb") as f:
        for _ in range(size_bytes // (1024 * 1024)):
            f.write(os.urandom(1024 * 1024))
        restante = size_bytes % (1024 * 1024)
        if restante:
            f.write(os.urandom(restante))

def calcular_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    hash_sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def run_command(command):
    try:
        proc = subprocess.Popen(
            ["python", "-m", "cliente.main_cliente"],
            cwd=".",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = proc.communicate(input=command + "\nexit\n")
        status = "Success" if proc.returncode == 0 else "Error"
        if status == "Error":
            print(f"Erro ao executar comando '{command}':\n{stderr}")
        return stdout, status
    except Exception as e:
        print(f"Erro inesperado ao executar '{command}': {e}")
        return "", "Error"

def benchmark():
    with open(csv_file, "w", newline="") as csvfile:
        fieldnames = [
            "File Size", "Operation", "Time (s)", "Throughput (MB/s)",
            "Status", "Bytes Transferidos", "Observações"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for label, size in file_sizes.items():
            filename = f"{label}.bin"
            filepath = os.path.join(test_dir, filename)

            # Gerar o arquivo
            generate_file(filepath, size)
            time.sleep(2)

            # Calcular hash original
            hash_original = calcular_sha256(filepath)

            # --- UPLOAD ---
            print(f"\n--- UPLOAD {filename} ---")
            start = time.time()
            _, status_upload = run_command(UPLOAD_COMMAND.format(filename=filepath))
            end = time.time()
            elapsed = end - start
            throughput = (size / (1024 * 1024)) / elapsed
            writer.writerow({
                "File Size": label,
                "Operation": "Upload",
                "Time (s)": round(elapsed, 2),
                "Throughput (MB/s)": round(throughput, 2),
                "Status": status_upload,
                "Bytes Transferidos": size,
                "Observações": ""
            })

            #tempo para replicação
            for i in range(25, 0, -1):
                pontos = '.' * (26 - i)  
                mensagem = f"aguardando {i}s {pontos}"
                print(f"\r{mensagem}", end='')
                sys.stdout.flush()
                time.sleep(1)
                

            # --- DOWNLOAD ---
            print(f"\n--- DOWNLOAD {filename} ---")
            start = time.time()
            _, status_download = run_command(DOWNLOAD_COMMAND.format(filename=filename))
            end = time.time()
            elapsed = end - start
            throughput = (size / (1024 * 1024)) / elapsed

            # Verificar arquivo baixado
            downloaded_path = os.path.join("cliente", "arquivos_download_cliente", filename)
            hash_downloaded = calcular_sha256(downloaded_path)
            sha_check = "OK" if hash_original == hash_downloaded else "FAIL"
            tamanho_real = os.path.getsize(downloaded_path) if os.path.exists(downloaded_path) else 0

            writer.writerow({
                "File Size": label,
                "Operation": "Download",
                "Time (s)": round(elapsed, 2),
                "Throughput (MB/s)": round(throughput, 2),
                "Status": status_download,
                "Bytes Transferidos": tamanho_real,
                "Observações": ""
            })

    print(f"\nBenchmark concluído. Resultados salvos em: {csv_file}")

if __name__ == "__main__":
    benchmark()

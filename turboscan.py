import asyncio
import socket
import sys
import time
import argparse
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

PORTS_DATABASE = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPCBIND", 135: "MSRPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 3306: "MySQL",
    3389: "RDP", 5900: "VNC", 8080: "HTTP-ALT"
}

CAT_ASCII = f"""
{Fore.CYAN}      /\\_/\\
     ( o.o )
      > ^ <  {Fore.YELLOW}TURBOSCAN v1.2.0{Fore.CYAN}
     /     \\
    |       |  {Style.DIM}Author -> l4st{Fore.CYAN}
    (___)___){Style.RESET_ALL}
"""

class TurboScanner:
    def __init__(self, target: str, ports: list, concurrency: int, timeout: float, verbose: bool):
        self.target = target
        self.ports = ports
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.verbose = verbose
        self.resolved_ip = ""

    def resolve(self):
        try:
            self.resolved_ip = socket.gethostbyname(self.target)
            return self.resolved_ip
        except socket.gaierror:
            print(f"{Fore.RED}[-] Falha crítica: Não foi possível resolver o host: {self.target}{Style.RESET_ALL}")
            sys.exit(1)

    async def _scan(self, port: int):
        async with self.semaphore:
            if self.verbose:
                print(f"{Fore.BLUE}[*] A testar porta: {port}...{Style.RESET_ALL}")

            try:
                conn = asyncio.open_connection(self.resolved_ip, port)
                reader, writer = await asyncio.wait_for(conn, timeout=self.timeout)

                service = PORTS_DATABASE.get(port, "unknown")

                try:
                    writer.close()
                    await writer.wait_closed()
                except:
                    pass

                print(f"{Fore.GREEN}[+] {port}/TCP aberta ({service}){Style.RESET_ALL}")
                return {"port": port, "service": service, "state": "open"}

            except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
                return None

    async def run(self):
        self.resolve()
        tasks = [self._scan(p) for p in self.ports]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

def parse_port_range(port_str: str) -> list:
    ports = []
    try:
        for part in port_str.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part))
        return sorted(list(set(ports)))
    except ValueError:
        print(f"{Fore.RED}[-] Erro: Intervalo de portas inválido (Ex: 22,80,1-1000){Style.RESET_ALL}")
        sys.exit(1)

def write_output_file(filepath: str, target: str, ip: str, results: list, elapsed: float):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# =========================================================\n")
        f.write(f"# TURBOSCAN REPORT - Generated on {now}\n")
        f.write(f"# Target: {target} ({ip})\n")
        f.write(f"# Scan completed in {elapsed:.2f} seconds\n")
        f.write("# =========================================================\n\n")

        f.write(f"{'PORT':<10} {'STATE':<10} {'SERVICE':<15}\n")
        f.write("-" * 35 + "\n")
        for r in results:
            f.write(f"{r['port']:<10} {'open':<10} {r['service']:<15}\n")

def main():
    print(CAT_ASCII)

    parser = argparse.ArgumentParser(description="TurboScan - Port Scanner Estável e Veloz")
    parser.add_argument("--ip", required=True, help="IP do alvo ou domínio")
    parser.add_argument("-p", "--ports", default="1-1024", help="Portas a escanear (Ex: 22,80-443)")
    parser.add_argument("-c", "--concurrency", type=int, default=1000, help="Conexões paralelas simultâneas")
    parser.add_argument("-t", "--timeout", type=float, default=1.0, help="Timeout de conexão em segundos")
    parser.add_argument("-v", "--verbose", action="store_true", help="Ativar modo de log verboso")
    parser.add_argument("-oN", help="Guardar o output num ficheiro com extensão personalizada .turboscan")

    args = parser.parse_args()
    ports_to_scan = parse_port_range(args.ports)

    scanner = TurboScanner(
        target=args.ip,
        ports=ports_to_scan,
        concurrency=args.concurrency,
        timeout=args.timeout,
        verbose=args.verbose
    )

    print(f"[*] A iniciar o scan em {Fore.YELLOW}{args.ip}{Style.RESET_ALL}")
    print(f"[*] {len(ports_to_scan)} portas em fila de espera...")
    print("-" * 55)

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    start_time = time.time()

    try:
        results = asyncio.run(scanner.run())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Scan abortado pelo utilizador. A fechar conexões...{Style.RESET_ALL}")
        sys.exit(0)

    elapsed = time.time() - start_time

    print("-" * 55)
    print(f"[*] Varredura concluída em {Fore.CYAN}{elapsed:.2f}s{Style.RESET_ALL}.")
    print(f"[*] Portas abertas detetadas: {Fore.GREEN}{len(results)}{Style.RESET_ALL}")

    if args.oN:
        filepath = args.oN if args.oN.endswith(".turboscan") else f"{args.oN}.turboscan"
        write_output_file(filepath, args.ip, scanner.resolved_ip, results, elapsed)
        print(f"{Fore.MAGENTA}[+] Relatório guardado em: {filepath}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

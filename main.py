import platform
import subprocess
import os
import datetime

# Tentativa de importar o psutil de forma segura em qualquer ambiente (LiveCD)
try:
    import psutil
except ImportError:
    psutil = None

def rodar_comando(comando):
    """Executa comandos do terminal com segurança e previne travamentos"""
    try:
        return subprocess.check_output(comando, shell=True, stderr=subprocess.DEVNULL).decode('cp850' if platform.system() == "Windows" else 'utf-8').strip()
    except:
        return ""

def limpar_nome(nome):
    """Passa um pente fino no texto bruto para remover termos redundantes"""
    if not nome: return "Não identificado"
    remover = ["Intel Corporation", "Advanced Micro Devices, Inc.", "[AMD/ATI]", "Controller", "Processor", "Graphics", "Audio", "Network"]
    resultado = nome
    for termo in remover:
        resultado = resultado.replace(termo, "")
    return " ".join(resultado.split()).strip()

def extrair_ano_bios(sistema):
    """Busca o ano gravado na BIOS de forma nativa dependendo do OS"""
    if sistema == "Linux":
        data_bruta = rodar_comando("cat /sys/class/dmi/id/bios_date 2>/dev/null") or rodar_comando("dmidecode -s bios-release-date 2>/dev/null")
        if "/" in data_bruta: return data_bruta.split("/")[-1].strip()
        if "-" in data_bruta: return data_bruta.split("-").strip()
    elif sistema == "Windows":
        data_windows = rodar_comando("wmic bios get releasedate /value").replace("ReleaseDate=", "").strip()
        if len(data_windows) >= 4: return data_windows[:4]
    return "Não detectado"

def obter_cpu_flags_linux():
    """Vaide de forma silenciosa verificar as instruções ocultas do processador"""
    try:
        with open("/proc/cpuinfo", "r") as f:
            for linha in f:
                if linha.strip().startswith("flags"):
                    return linha.split(":")[-1].strip().lower()
    except: pass
    return ""
def gerar_relatorio():
    sistema = platform.system()
    kernel = platform.release()
    arquitetura = platform.machine()
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 1. Identificação da Máquina e Fabricante
    modelo_pc, fabricante = "Generico-Montado", "Desconhecido"
    if sistema == "Linux":
        modelo_pc = rodar_comando("cat /sys/class/dmi/id/product_name 2>/dev/null") or "Generico-Montado"
        fabricante = rodar_comando("cat /sys/class/dmi/id/sys_vendor 2>/dev/null") or "Desconhecido"
    elif sistema == "Windows":
        modelo_pc = rodar_comando("wmic computersystem get model /value").replace("Model=", "") or "Generico-Montado"
        fabricante = rodar_comando("wmic computersystem get manufacturer /value").replace("Manufacturer=", "") or "Desconhecido"
        
    ano_bios = extrair_ano_bios(sistema)
    
    # 2. Processador e Temperatura
    cpu_real = platform.processor()
    if sistema == "Linux":
        cpu_bruta = rodar_comando("lscpu | grep 'Model name' | cut -d: -f2") or rodar_comando("lscpu | grep 'Nome do modelo' | cut -d: -f2")
        if cpu_bruta: cpu_real = limpar_nome(cpu_bruta)
    elif sistema == "Windows":
        cpu_bruta = rodar_comando("wmic cpu get name /value").replace("Name=", "")
        if cpu_bruta: cpu_real = limpar_nome(cpu_bruta)
    
    temp_cpu = "N/A"
    if sistema == "Linux" and os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_cpu = f"{int(f.read().strip()) // 1000}°C"
        except: pass

    # 3. Memória RAM (Proteção contra falta de pacote)
    if psutil:
        ram_total_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    else:
        if sistema == "Linux":
            ram_total_gb = round(int(rodar_comando("awk '/MemTotal/ {print $2}' /proc/meminfo")) / (1024 ** 2), 1)
        else:
            ram_total_gb = "N/A (Requer compilado)"
    
    # 4. Diagnósticos Auxiliares (Energia, Boot e Rede)
    status_energia = "Alimentação Direta (Desktop)"
    if sistema == "Linux" and (os.path.exists("/sys/class/power_supply/BAT0") or os.path.exists("/sys/class/power_supply/BAT1")):
        cap = rodar_comando("cat /sys/class/power_supply/BAT*/capacity 2>/dev/null | head -n 1")
        tomada = rodar_comando("cat /sys/class/power_supply/AC*/online 2>/dev/null | head -n 1")
        status_energia = f"Notebook (Bateria: {cap}% - Conectado)" if tomada == "1" else f"⚠️ Notebook (Bateria: {cap}% - FORA DA TOMADA)"
    elif sistema == "Windows":
        bateria = rodar_comando("wmic path win32_battery get estimatechargeremaining /value").replace("EstimateChargeRemaining=", "")
        if bateria: status_energia = f"Notebook (Bateria: {bateria}%)"

    modo_boot = "Desconhecido"
    if sistema == "Linux": modo_boot = "UEFI" if os.path.exists("/sys/firmware/efi") else "Legacy (BIOS)"
    elif sistema == "Windows": modo_boot = rodar_comando("powershell -command \"$env:firmware_type\"") or "Detectado via OS"
        
    ping_cmd = ["ping", "-n" if sistema == "Windows" else "-c", "1", "8.8.8.8"]
    status_rede = "Conectado à Internet" if subprocess.run(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0 else "Sem Internet (Verificar Driver/Cabo)"

    # 5. Varredura de Chips
    gpus, audios, redes = [], [], []
    if sistema == "Linux":
        gpus = [limpar_nome(g) for g in rodar_comando("lspci 2>/dev/null | grep -E 'VGA|3D' | cut -d: -f3").split('\n') if g.strip()]
        audios = [limpar_nome(a) for a in rodar_comando("lspci 2>/dev/null | grep -E -i 'audio|sound' | cut -d: -f3").split('\n') if a.strip()]
        redes = [limpar_nome(r) for r in rodar_comando("lspci 2>/dev/null | grep -E -i 'ethernet|network|wireless|wi-fi' | cut -d: -f3").split('\n') if r.strip()]
    elif sistema == "Windows":
        gpus = [limpar_nome(g.replace("Name=", "")) for g in rodar_comando("wmic path win32_VideoController get Name /value").split('\n') if g.strip()]
        audios = [limpar_nome(a.replace("Name=", "")) for a in rodar_comando("wmic path win32_SoundDevice get Name /value").split('\n') if a.strip()]
        redes = [limpar_nome(r.replace("Name=", "")) for r in rodar_comando("wmic path win32_NetworkAdapter where \"PhysicalAdapter=True\" get Name /value").split('\n') if r.strip()]

    # 6. Avaliação da Geração da CPU (AVX / AVX2)
    cpu_flags = obter_cpu_flags_linux()
    era_cpu, rec_kernel, motivo, kernels_legados = "Mapeamento Padrão", "Ajustado por OS", "Uso de Ferramenta Nativa", "N/A"
    if sistema == "Linux":
        if "64" not in arquitetura or arquitetura != "x86_64":
            era_cpu = "Antiga (Arquitetura 32-bits legada)"
            rec_kernel = "Kernel LTS Antigo de 32-bits (Série 5.4 / 4.19 ou inferior)"
            motivo = f"Processador legado operando em 32-bits ({arquitetura}). Distribuições modernas padrão não darão boot."
            kernels_legados = "• Kernel 4.19.x (Suporte encerrado em 2024)\n• Kernel 3.16.x (Suporte encerrado em 2020)"
        elif "avx" not in cpu_flags:
            era_cpu = "Pré-2011 ou Entrada (Sem suporte a instruções AVX)"
            rec_kernel = "Kernel 5.15 LTS ou Kernel 6.1 LTS"
            motivo = "Processador antigo de baixo custo (sem AVX). Kernels estáveis maduros pouparão processamento em background."
            kernels_legados = "• Kernel 5.4.x (Suporte encerrado em 2025)\n• Kernel 4.19.x (Suporte encerrado em 2024)"
        elif "avx" in cpu_flags and "avx2" not in cpu_flags:
            era_cpu = "Intermediária / Anos 2011-2013 (Possui AVX clássico)"
            rec_kernel = "Kernel 6.1 LTS ou Kernel 6.6 LTS"
            motivo = "Processador intermediário de 64-bits (Era Sandy Bridge/Ivy Bridge). Excelente estabilidade com as séries estáveis 6.1 e 6.6."
            kernels_legados = "• Kernel 5.10.x (Suporte estendido até 2026)\n• Kernel 4.19.x (Suporte encerrado em 2024)"
        elif "avx2" in cpu_flags:
            era_cpu = "Moderna / Pós-2014 (Possui conjunto de instruções completo AVX2+)"
            if isinstance(ram_total_gb, float) and ram_total_gb >= 8:
                rec_kernel = "Kernel Zen / Liquorix (Otimizados) ou Kernels LTS Modernos (6.12 / 6.18)"
                motivo = f"Processador moderno completo (AVX2+) com ampla memória RAM ({ram_total_gb} GB). Suporta agendadores de alto desempenho."
            else:
                rec_kernel = "Kernel Standard Stable (Padrão Atual) ou Kernel 6.12 LTS"
                motivo = f"Processador moderno com instruções AVX2, porém limitado pela quantidade de RAM ({ram_total_gb} GB)."
            kernels_legados = "• Kernel 5.15.x (Suporte estendido até 2026)\n• Kernel 5.10.x (Suporte estendido até 2026)"

    return sistema, arquitetura, modo_boot, data_atual, status_rede, status_energia, modelo_pc, fabricante, ano_bios, cpu_real, temp_cpu, ram_total_gb, era_cpu, rec_kernel, motivo, kernels_legados, audios, redes, gpus
def mostrar_e_salvar():
    # Desempacota todas as variáveis coletadas na Caixa 2
    sistema, arquitetura, modo_boot, data_atual, status_rede, status_energia, modelo_pc, fabricante, ano_bios, cpu_real, temp_cpu, ram_total_gb, era_cpu, rec_kernel, motivo, kernels_legados, audios, redes, gpus = gerar_relatorio()
    
    largura = 85
    linhas = []
    def add(texto=""): linhas.append(texto)
    
    add("=" * largura)
    add("      DIAGNÓSTICO DE HARDWARE :(VERSÃO PYTHON DE BANCADA) : BY ELEMENTISTA      ")
    add("=" * largura)
    add(f"💿 OS Rodando no momento : {sistema} ({arquitetura})")
    add(f"📟 Inicialização          : {modo_boot:<30} | 📅 Data: {data_atual}")
    add(f"🌐 Conectividade          : {status_rede:<30} | 🔋 Energia: {status_energia}")
    add("-" * largura)
    add("📋 INFORMAÇÃO DO EQUIPAMENTO & COMPONENTES EMBUTIDOS:")
    add("-" * largura)
    add(f"💻 Equipamento            : {modelo_pc.strip()} ({fabricante.strip()})")
    add(f"📅 Ano da Placa-Mãe (BIOS): {ano_bios}")
    add(f"🧠 Processador            : {cpu_real} ({temp_cpu})")
    if sistema == "Linux": add(f"⏳ Era da CPU             : {era_cpu}")
    add(f"📟 Memória RAM            : {ram_total_gb} GB Total")
    add("-" * largura)
    add("🔊 Controladores de Áudio Embutidos:")
    for a in audios: add(f"  • {a}")
    add("-" * largura)
    add("🌐 Controladores de Rede (Ethernet/Wi-Fi):")
    for r in redes: add(f"  • {r}")
    add("-" * largura)
    add("🎮 Vídeo (GPU) Detectado:")
    for g in gpus: add(f"  • {g}")
    
    if sistema == "Linux":
        add("-" * largura)
        add("🎯 RECOMENDAÇÃO DE KERNEL LINUX PARA INSTALAÇÃO DEFINITIVA:")
        add("-" * largura)
        add(f"👉 Usar Atual: {rec_kernel}")
        add(f"💡 Motivo: {motivo}")
        add("=" * largura)
        if arquitetura == "x86_64":
            add("📌 VERSÕES DO KERNEL EM SUPORTE ATIVO (MERCADO ATUAL):")
            add("• Linha Estável / Recente: Kernel 7.2.x (Suporte Ativo)")
            add("• Longo Termo (LTS): Kernel 6.18.x (Suporte Ativo - Até 2028)")
            add("• Longo Termo (LTS): Kernel 6.12.x (Suporte Ativo - Até 2028)")
            add("=" * largura)
        add("⚠️ SÉRIES DE KERNELS MAIS ANTIGOS COMPATÍVEIS COM ESTA CPU:")
        add("-" * largura)
        add(kernels_legados)
    add("=" * largura)

    conteudo_final = "\n".join(linhas)
    print(conteudo_final)
    
    resposta = input("\n💾 Deseja salvar este relatório em um arquivo de texto agora? [s/N]: ").strip().lower()
    if resposta == 's':
        pasta_logs = os.path.join(os.getcwd(), "diagnosticos_bancada")
        os.makedirs(pasta_logs, exist_ok=True)
        modelo_limpo = "".join([c for c in modelo_pc if c.isalnum() or c in ("-", "_")]).strip() or "Maquina_Generica"
        data_log = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        caminho_final = os.path.join(pasta_logs, f"diagnostico_{modelo_limpo}_{data_log}.txt")
        
        with open(caminho_final, "w") as f:
            f.write(conteudo_final)
        print("-" * largura)
        print(f"✅ Relatório salvo com sucesso em:\n📂 {caminho_final}\n" + "=" * largura)
    else:
        print("\nℹ️ Operação concluída. Informações mantidas apenas na tela.")
    input("\nPressione ENTER para fechar...")

if __name__ == "__main__":
    mostrar_e_salvar()

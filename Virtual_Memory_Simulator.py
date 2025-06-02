import sys
import os
import time
import json
import argparse
from collections import deque, OrderedDict, defaultdict
from datetime import datetime
from tqdm import tqdm
import threading
import queue

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    PURPLE = '\033[35m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    GOLD = '\033[93m'

def print_banner():
    banner = f"""
{Colors.BOLD}{Colors.GREEN}
    ╔═══════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                           ║
    ║                  ███╗   ███╗███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗                 ║
    ║                  ████╗ ████║██╔════╝████╗ ████║██╔═══██╗██╔══██╗╚██╗ ██╔╝                 ║
    ║                  ██╔████╔██║█████╗  ██╔████╔██║██║   ██║██████╔╝ ╚████╔╝                  ║
    ║                  ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║██╔══██╗  ╚██╔╝                   ║
    ║                  ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║                    ║
    ║                  ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝                    ║
    ║                                                                                           ║
    ║            ███████╗██╗███╗   ███╗██╗   ██╗██╗      █████╗ ████████╗ ██████╗ ██████╗       ║
    ║            ██╔════╝██║████╗ ████║██║   ██║██║     ██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗      ║
    ║            ███████╗██║██╔████╔██║██║   ██║██║     ███████║   ██║   ██║   ██║██████╔╝      ║
    ║            ╚════██║██║██║╚██╔╝██║██║   ██║██║     ██╔══██║   ██║   ██║   ██║██╔══██╗      ║
    ║            ███████║██║██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║      ║
    ║            ╚══════╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝      ║
    ║                                                                                           ║
    ║                        🚀 SIMULADOR AVANZADO DE GESTIÓN DE MEMORIA 🚀                     ║
    ║                               💻 VIRTUAL MEMORY MANAGER 💻                                ║
    ║                                   ⚡ VÍCTOR ROMERO ⚡                                     ║
    ║                                         12211079                                          ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}"""
    print(banner)

def print_section_header(title, color=Colors.OKBLUE):
    width = 80
    padding = (width - len(title) - 4) // 2
    print(f"\n{color}{'═' * width}")
    print(f"║{' ' * padding}🔥 {title} 🔥{' ' * padding}║")
    print(f"{'═' * width}{Colors.ENDC}")

def print_table(headers, rows, title=None, colors=None):
    if title:
        print(f"\n{Colors.BOLD}{Colors.CYAN}📊 {title} 📊{Colors.ENDC}")
    
    if not colors:
        colors = [Colors.WHITE] * len(headers)
    
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(str(header))
        for row in rows:
            if i < len(row):
                max_width = max(max_width, len(str(row[i])))
        col_widths.append(max_width + 2)
 
    line = "┌" + "┬".join("─" * width for width in col_widths) + "┐"
    print(f"{Colors.BOLD}{Colors.CYAN}{line}{Colors.ENDC}")
    
    header_line = "│"
    for i, (header, width, color) in enumerate(zip(headers, col_widths, colors)):
        header_line += f"{color}{str(header).center(width)}{Colors.ENDC}│"
    print(header_line)
    
    line = "├" + "┼".join("─" * width for width in col_widths) + "┤"
    print(f"{Colors.BOLD}{Colors.CYAN}{line}{Colors.ENDC}")
    
    for row in rows:
        row_line = "│"
        for i, (cell, width) in enumerate(zip(row, col_widths)):
            color = colors[i] if i < len(colors) else Colors.WHITE
            cell_str = str(cell).rjust(width-1) + " "
            row_line += f"{color}{cell_str}{Colors.ENDC}│"
        print(row_line)
  
    line = "└" + "┴".join("─" * width for width in col_widths) + "┘"
    print(f"{Colors.BOLD}{Colors.CYAN}{line}{Colors.ENDC}")

def print_progress_bar(current, total, description="Progreso", width=50):
    """Barra de progreso"""
    progress = int(width * current / total)
    bar = "█" * progress + "░" * (width - progress)
    percentage = (current / total) * 100
    
    print(f"\r{Colors.BOLD}{Colors.CYAN}{description}: {Colors.YELLOW}[{bar}] {percentage:.1f}% ({current:,}/{total:,}){Colors.ENDC}", end="", flush=True)

class MemoryReference:
    __slots__ = ['address', 'operation', 'page_num']
    
    def __init__(self, address, operation):
        self.address = address
        self.operation = operation
        self.page_num = address >> 12

class AdvancedPagedMemoryManager:
    def __init__(self, frame_count, replacement_policy):
        self.frame_count = frame_count
        self.replacement_policy = replacement_policy
        self.page_table = {}
        self.frame_table = {}
        self.dirty_pages = set()
       
        self.page_faults = 0
        self.disk_writes = 0
        self.replacements = 0
        self.hits = 0
        self.total_accesses = 0
        self.operation_stats = {'R': 0, 'W': 0}
        self.page_access_frequency = defaultdict(int)
        self.temporal_locality = []
        self.spatial_locality = []
        
        #STRUCTS Especificas de Polcies
        if replacement_policy == "FIFO":
            self.fifo_queue = deque()
        elif replacement_policy == "LRU":
            self.lru_cache = OrderedDict()
        elif replacement_policy == "LFU":
            self.lfu_counter = defaultdict(int)
            self.lfu_time = defaultdict(int)
        elif replacement_policy == "CLOCK":
            self.clock_hand = 0
            self.clock_bits = {}
        elif replacement_policy == "OPT":
            self.opt_data = {
                'future_refs': {},
                'current_pos': 0
            }
    
    def preprocess_opt(self, filepath):
        """Preprocesa el archivo para OPT"""
        print_section_header("PREPROCESANDO PARA ALGORITMO ÓPTIMO")
        
        start_time = time.time()
        total_lines = self.count_lines_fast(filepath)
        
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f):
                if line_num % 50000 == 0:
                    print_progress_bar(line_num, total_lines, "Analizando referencias futuras")
                
                parts = line.strip().split()
                if len(parts) == 2:
                    address = int(parts[0], 16)
                    page_num = address >> 12
                    if page_num not in self.opt_data['future_refs']:
                        self.opt_data['future_refs'][page_num] = []
                    self.opt_data['future_refs'][page_num].append(line_num)
        
        print_progress_bar(total_lines, total_lines, "Analizando referencias futuras")
        elapsed = time.time() - start_time
        print(f"\n{Colors.OKGREEN}✅ Preprocesamiento completado en {elapsed:.2f} segundos{Colors.ENDC}")
    
    def count_lines_fast(self, filepath):
        """Cuenta líneas de forma rápida"""
        with open(filepath, 'r') as f:
            return sum(1 for _ in f)
    
    def access_page(self, page_num, operation, current_pos=None):
        self.total_accesses += 1
        self.operation_stats[operation] += 1
        self.page_access_frequency[page_num] += 1
        
        if page_num in self.page_table:
            # Hit de página
            self.hits += 1
            frame_num = self.page_table[page_num]
            
            # Actualizar estructuras de política
            if self.replacement_policy == "LRU":
                self.lru_cache.move_to_end(page_num)
            elif self.replacement_policy == "LFU":
                self.lfu_counter[page_num] += 1
                self.lfu_time[page_num] = self.total_accesses
            elif self.replacement_policy == "CLOCK":
                self.clock_bits[page_num] = 1
            
            if operation == 'W':
                self.frame_table[frame_num]['dirty'] = True
                self.dirty_pages.add(page_num)
            
            return frame_num
        else:
            # Page fault
            self.page_faults += 1
            return self.handle_page_fault(page_num, operation, current_pos)
    
    def handle_page_fault(self, page_num, operation, current_pos=None):
        if len(self.page_table) < self.frame_count:
            # Avilable Frames
            frame_num = len(self.page_table)
        else:
            # Reemplazo
            self.replacements += 1
            frame_num = self.select_victim_frame(current_pos)
            victim_page = self.frame_table[frame_num]['page_num']
            
            if self.frame_table[frame_num]['dirty']:
                self.disk_writes += 1
            
            # Clean STRUCTS
            del self.page_table[victim_page]
            if victim_page in self.dirty_pages:
                self.dirty_pages.remove(victim_page)
            if self.replacement_policy == "CLOCK" and victim_page in self.clock_bits:
                del self.clock_bits[victim_page]
        
        # NEW PAGE 
        self.page_table[page_num] = frame_num
        self.frame_table[frame_num] = {
            'page_num': page_num,
            'dirty': (operation == 'W')
        }
        
        if operation == 'W':
            self.dirty_pages.add(page_num)
        
        # Actualizar estructuras de política
        if self.replacement_policy == "FIFO":
            self.fifo_queue.append(page_num)
        elif self.replacement_policy == "LRU":
            self.lru_cache[page_num] = frame_num
        elif self.replacement_policy == "LFU":
            self.lfu_counter[page_num] += 1
            self.lfu_time[page_num] = self.total_accesses
        elif self.replacement_policy == "CLOCK":
            self.clock_bits[page_num] = 1
        
        return frame_num
    
    def select_victim_frame(self, current_pos=None):
        if self.replacement_policy == "FIFO":
            victim_page = self.fifo_queue.popleft()
            return self.page_table[victim_page]
        
        elif self.replacement_policy == "LRU":
            victim_page, _ = self.lru_cache.popitem(last=False)
            return self.page_table[victim_page]
        
        elif self.replacement_policy == "LFU":
            # Encontrar página con menor frecuencia, y en caso de empate, la más antigua
            min_freq = min(self.lfu_counter[page] for page in self.page_table)
            candidates = [page for page in self.page_table if self.lfu_counter[page] == min_freq]
            victim_page = min(candidates, key=lambda p: self.lfu_time[p])
            return self.page_table[victim_page]
        
        elif self.replacement_policy == "CLOCK":
            while True:
                pages = list(self.page_table.keys())
                if not pages:
                    return 0
                
                current_page = pages[self.clock_hand % len(pages)]
                
                if self.clock_bits.get(current_page, 0) == 0:
                    victim_frame = self.page_table[current_page]
                    self.clock_hand = (self.clock_hand + 1) % len(pages)
                    return victim_frame
                else:
                    self.clock_bits[current_page] = 0
                    self.clock_hand = (self.clock_hand + 1) % len(pages)
        
        elif self.replacement_policy == "OPT":
            farthest = -1
            victim_page = None
            
            for page in self.page_table:
                refs = self.opt_data['future_refs'].get(page, [])
                next_use = None
                
                for ref_pos in refs:
                    if ref_pos > current_pos:
                        next_use = ref_pos
                        break
                
                if next_use is None:
                    return self.page_table[page]
                
                if next_use > farthest:
                    farthest = next_use
                    victim_page = page
            
            return self.page_table.get(victim_page, 0)
        
        return 0
    
    def get_statistics(self):
        """Calcula estadísticas avanzadas"""
        if self.total_accesses == 0:
            return {}
        
        hit_rate = (self.hits / self.total_accesses) * 100
        fault_rate = (self.page_faults / self.total_accesses) * 100
        replacement_rate = (self.replacements / self.total_accesses) * 100
        
        # Effective Access Time
        eat = 100 + (fault_rate / 100 * 10000000)  # 100ns + fault_rate * 10ms
        
        return {
            'total_accesses': self.total_accesses,
            'hits': self.hits,
            'page_faults': self.page_faults,
            'replacements': self.replacements,
            'disk_writes': self.disk_writes,
            'hit_rate': hit_rate,
            'fault_rate': fault_rate,
            'replacement_rate': replacement_rate,
            'eat': eat,
            'reads': self.operation_stats['R'],
            'writes': self.operation_stats['W'],
            'unique_pages': len(self.page_access_frequency),
            'avg_page_accesses': sum(self.page_access_frequency.values()) / len(self.page_access_frequency) if self.page_access_frequency else 0
        }

def process_trace_file_advanced(filepath, frame_counts, policies, show_realtime=False):
    """Procesa el archivo de traza con estadísticas avanzadas"""
    print_section_header("INICIANDO SIMULACIÓN AVANZADA")
    
    total_lines = 0
    with open(filepath, 'r') as f:
        total_lines = sum(1 for _ in f)
    
    file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
    print(f"{Colors.BOLD}{Colors.CYAN}📁 Archivo: {Colors.WHITE}{filepath}")
    print(f"{Colors.CYAN}📊 Referencias totales: {Colors.WHITE}{total_lines:,}")
    print(f"{Colors.CYAN}💾 Tamaño del archivo: {Colors.WHITE}{file_size:.2f} MB{Colors.ENDC}")
    
    all_results = []
    
    for frames in frame_counts:
        for policy in policies:
            print_section_header(f"SIMULANDO {policy} CON {frames} FRAMES")
            
            start_time = time.time()
            manager = AdvancedPagedMemoryManager(frames, policy)
            
            if policy == "OPT":
                manager.preprocess_opt(filepath)
            
            # Simulación línea por línea
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(f):
                    if line_num % 10000 == 0:
                        print_progress_bar(line_num, total_lines, f"Procesando {policy}")
                    
                    parts = line.strip().split()
                    if len(parts) == 2:
                        address = int(parts[0], 16)
                        operation = parts[1]
                        page_num = address >> 12
                        manager.access_page(page_num, operation, line_num)
            
            print_progress_bar(total_lines, total_lines, f"Procesando {policy}")
            elapsed = time.time() - start_time
            
            stats = manager.get_statistics()
            stats.update({
                'frames': frames,
                'policy': policy,
                'execution_time': elapsed
            })
            
            all_results.append(stats)
            
            print(f"\n{Colors.OKGREEN}✅ Simulación completada en {elapsed:.2f} segundos{Colors.ENDC}")
            print_immediate_results(stats)
    
    return all_results

def print_immediate_results(stats):
    """Muestra resultados inmediatos de una simulación"""
    headers = ["Métrica", "Valor", "Descripción"]
    colors = [Colors.CYAN, Colors.YELLOW, Colors.WHITE]
    
    rows = [
        ["Page Faults", f"{stats['page_faults']:,}", "Fallos de página totales"],
        ["Hit Rate", f"{stats['hit_rate']:.2f}%", "Porcentaje de aciertos"],
        ["Fault Rate", f"{stats['fault_rate']:.2f}%", "Porcentaje de fallos"],
        ["Replacements", f"{stats['replacements']:,}", "Reemplazos realizados"],
        ["Disk Writes", f"{stats['disk_writes']:,}", "Escrituras a disco"],
        ["EAT", f"{stats['eat']:.2f} ns", "Tiempo acceso efectivo"],
        ["Reads/Writes", f"{stats['reads']:,}/{stats['writes']:,}", "Operaciones de lectura/escritura"],
        ["Unique Pages", f"{stats['unique_pages']:,}", "Páginas únicas accedidas"]
    ]
    
    print_table(headers, rows, f"Resultados {stats['policy']} - {stats['frames']} frames", colors)

def print_final_comparison(results):
    """Imprime una comparación final épica"""
    print_section_header("COMPARACIÓN FINAL DE RENDIMIENTO", Colors.OKGREEN)
    
    # Tabla principal de comparación
    headers = ["Frames", "Política", "Page Faults", "Hit Rate", "EAT (ns)", "Tiempo (s)"]
    colors = [Colors.CYAN, Colors.YELLOW, Colors.RED, Colors.GREEN, Colors.PURPLE, Colors.BLUE]
    
    rows = []
    for result in results:
        rows.append([
            result['frames'],
            result['policy'],
            f"{result['page_faults']:,}",
            f"{result['hit_rate']:.2f}%",
            f"{result['eat']:.2f}",
            f"{result['execution_time']:.2f}"
        ])
    
    print_table(headers, rows, "RESUMEN COMPLETO DE SIMULACIONES", colors)
    
    # Encontrar mejores rendimientos
    print_section_header("🏆 MEJORES RENDIMIENTOS", Colors.OKGREEN)
    
    best_hit_rate = max(results, key=lambda x: x['hit_rate'])
    best_eat = min(results, key=lambda x: x['eat'])
    best_time = min(results, key=lambda x: x['execution_time'])
    
    print(f"{Colors.BOLD}{Colors.GOLD}🥇 Mejor Hit Rate: {Colors.WHITE}{best_hit_rate['policy']} con {best_hit_rate['frames']} frames - {best_hit_rate['hit_rate']:.2f}%{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GOLD}🥇 Mejor EAT: {Colors.WHITE}{best_eat['policy']} con {best_eat['frames']} frames - {best_eat['eat']:.2f} ns{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GOLD}🥇 Más Rápido: {Colors.WHITE}{best_time['policy']} con {best_time['frames']} frames - {best_time['execution_time']:.2f}s{Colors.ENDC}")

def save_results_json(results, filename):
    """Guarda los resultados en formato JSON"""
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'results': results,
        'summary': {
            'total_simulations': len(results),
            'policies_tested': list(set(r['policy'] for r in results)),
            'frame_counts_tested': list(set(r['frames'] for r in results))
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"{Colors.OKGREEN}💾 Resultados guardados en: {filename}{Colors.ENDC}")

# Aprovechando Compi hice un parser de argumentos para la entrada de datos :D
def create_arg_parser():
    parser = argparse.ArgumentParser(
        description="🚀 Simulador Avanzado de Gestión de Memoria Virtual",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python epic_memory_sim.py trace.txt
  python epic_memory_sim.py trace.txt --frames 10 50 100 --policies FIFO LRU OPT
  python epic_memory_sim.py trace.txt --save-json results.json --realtime
        """
    )
    
    parser.add_argument('trace_file', help='Archivo de traza de memoria')
    parser.add_argument('--frames', nargs='+', type=int, default=[10, 50, 100],
                        help='Número de frames a probar (default: 10 50 100)')
    parser.add_argument('--policies', nargs='+', default=['FIFO', 'LRU', 'OPT'],
                        choices=['FIFO', 'LRU', 'LFU', 'CLOCK', 'OPT'],
                        help='Políticas de reemplazo a probar')
    parser.add_argument('--save-json', help='Guardar resultados en archivo JSON')
    parser.add_argument('--realtime', action='store_true',
                        help='Mostrar estadísticas en tiempo real')
    
    return parser

def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    
    print_banner()
    
    if not os.path.exists(args.trace_file):
        print(f"{Colors.FAIL}❌ Error: El archivo {args.trace_file} no existe{Colors.ENDC}")
        return 1
    
    print_section_header("CONFIGURACIÓN DE SIMULACIÓN")
    print(f"{Colors.BOLD}{Colors.CYAN}📁 Archivo de traza: {Colors.WHITE}{args.trace_file}")
    print(f"{Colors.CYAN}🔢 Frames a probar: {Colors.WHITE}{args.frames}")
    print(f"{Colors.CYAN}🔄 Políticas: {Colors.WHITE}{args.policies}")
    if args.save_json:
        print(f"{Colors.CYAN}💾 Guardar en: {Colors.WHITE}{args.save_json}")
    print(f"{Colors.CYAN}⏱️  Tiempo real: {Colors.WHITE}{'Sí' if args.realtime else 'No'}{Colors.ENDC}")
    
    # Procesar archivo
    start_total = time.time()
    results = process_trace_file_advanced(
        args.trace_file, 
        args.frames, 
        args.policies, 
        args.realtime
    )
    total_time = time.time() - start_total
    
    print_final_comparison(results)
    
    # STATS
    print_section_header("ESTADÍSTICAS DE EJECUCIÓN", Colors.PURPLE)
    print(f"{Colors.BOLD}{Colors.PURPLE}⏱️  Tiempo total de ejecución: {Colors.WHITE}{total_time:.2f} segundos")
    print(f"{Colors.PURPLE}🔢 Simulaciones completadas: {Colors.WHITE}{len(results)}")
    print(f"{Colors.PURPLE}⚡ Promedio por simulación: {Colors.WHITE}{total_time/len(results):.2f} segundos{Colors.ENDC}")
    
    if args.save_json:
        save_results_json(results, args.save_json)
    
    print(f"\n{Colors.BOLD}{Colors.OKGREEN}🎉 ¡SIMULACIÓN COMPLETADA EXITOSAMENTE! 🎉{Colors.ENDC}")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Simulación interrumpida por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Error inesperado: {str(e)}{Colors.ENDC}")
        sys.exit(1)
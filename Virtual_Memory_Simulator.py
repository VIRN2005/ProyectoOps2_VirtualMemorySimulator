import sys
from collections import deque, OrderedDict
import mmap
import os
import time
from tqdm import tqdm  

class MemoryReference:
    __slots__ = ['address', 'operation', 'page_num']  
    
    def __init__(self, address, operation):
        self.address = address
        self.operation = operation
        self.page_num = address >> 12 

class PagedMemoryManager:
    def __init__(self, frame_count, replacement_policy):
        self.frame_count = frame_count
        self.replacement_policy = replacement_policy
        self.page_table = {} 
        self.frame_table = {}
        self.dirty_pages = set()
        self.page_faults = 0
        self.disk_writes = 0
        self.replacements = 0
        
        if replacement_policy == "FIFO":
            self.fifo_queue = deque(maxlen=frame_count * 2)
        elif replacement_policy == "LRU":
            self.lru_cache = OrderedDict()
        elif replacement_policy == "OPT":
            self.opt_data = {
                'future_refs': {},
                'current_pos': 0
            }
    
    def preprocess_opt(self, filepath):
        """Preprocesa el archivo para OPT (solo ejecutar para OPT)"""
        print("Preprocesando referencias para OPT...")
        start_time = time.time()
        
        total_lines = 0
        with open(filepath, 'r') as f:
            for _ in f:
                total_lines += 1
        
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(tqdm(f, total=total_lines, desc="Preprocesamiento OPT")):
                parts = line.strip().split()
                if len(parts) == 2:
                    address = int(parts[0], 16)
                    page_num = address >> 12
                    if page_num not in self.opt_data['future_refs']:
                        self.opt_data['future_refs'][page_num] = []
                    self.opt_data['future_refs'][page_num].append(line_num)
        
        print(f"Preprocesamiento OPT completado en {time.time() - start_time:.2f} segundos")
    
    def access_page(self, page_num, operation, current_pos=None):
        if page_num in self.page_table:
            # Hit de página
            frame_num = self.page_table[page_num]
            if self.replacement_policy == "LRU":
                self.lru_cache.move_to_end(page_num)
            if operation == 'W':
                self.frame_table[frame_num]['dirty'] = True
            return frame_num
        else:
            self.page_faults += 1
            return self.handle_page_fault(page_num, operation, current_pos)
    
    def handle_page_fault(self, page_num, operation, current_pos=None):
        if len(self.page_table) < self.frame_count:
            frame_num = len(self.page_table)
        else:
            self.replacements += 1
            frame_num = self.select_victim_frame(current_pos)
            victim_page = self.frame_table[frame_num]['page_num']
            
            if self.frame_table[frame_num]['dirty']:
                self.disk_writes += 1
            
            del self.page_table[victim_page]
            if victim_page in self.dirty_pages:
                self.dirty_pages.remove(victim_page)
        
        self.page_table[page_num] = frame_num
        self.frame_table[frame_num] = {
            'page_num': page_num,
            'dirty': (operation == 'W')
        }
        
        if operation == 'W':
            self.dirty_pages.add(page_num)
        
        # POLICIES
        if self.replacement_policy == "FIFO":
            self.fifo_queue.append(page_num)
        elif self.replacement_policy == "LRU":
            self.lru_cache[page_num] = frame_num
            self.lru_cache.move_to_end(page_num)
        
        return frame_num
    
    def select_victim_frame(self, current_pos=None):
        if self.replacement_policy == "FIFO":
            victim_page = self.fifo_queue.popleft()
            while victim_page not in self.page_table:
                victim_page = self.fifo_queue.popleft()
            return self.page_table[victim_page]
        elif self.replacement_policy == "LRU":
            victim_page, _ = self.lru_cache.popitem(last=False)
            return self.page_table[victim_page]
        elif self.replacement_policy == "OPT":
            farthest = -1
            victim_page = None
            
            for page in self.page_table:
                # NEXT REF
                refs = self.opt_data['future_refs'].get(page, [])
                next_use = None
                
                for ref_pos in refs:
                    if ref_pos > current_pos:
                        next_use = ref_pos
                        break
                
                if next_use is None:
                    # NO FUTURE REFS 
                    return self.page_table[page]
                
                if next_use > farthest:
                    farthest = next_use
                    victim_page = page
            
            return self.page_table.get(victim_page, 0)
        
        return 0 
    
    def calculate_eat(self, total_accesses):
        # SUPOSEDLY: Tiempo de acceso efectivo (asumiendo 100ns de acceso a memoria) y 10ms (10,000,000ns) para fallo de página
        page_fault_rate = self.page_faults / total_accesses
        return 100 + (page_fault_rate * 10000000)

def count_lines(filepath):
    """Cuenta líneas eficientemente en archivos grandes"""
    with open(filepath, 'r') as f:
        return sum(1 for _ in f)

def process_trace_file(filepath, frame_counts, policies):
    total_lines = count_lines(filepath)
    print(f"Procesando archivo {filepath} con {total_lines:,} referencias")
    
    results = []
    
    for frames in frame_counts:
        for policy in policies:
            print(f"\nConfiguración: {frames} frames, política {policy}")
            start_time = time.time()
            
            manager = PagedMemoryManager(frames, policy)
            if policy == "OPT":
                manager.preprocess_opt(filepath)
            
            # LINE-BY-LINE :V
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(tqdm(f, total=total_lines, desc=f"Simulando {policy} con {frames} frames")):
                    parts = line.strip().split()
                    if len(parts) == 2:
                        address = int(parts[0], 16)
                        operation = parts[1]
                        page_num = address >> 12
                        manager.access_page(page_num, operation, line_num)
            
            # Calcular métricas finales
            eat = manager.calculate_eat(total_lines)
            elapsed = time.time() - start_time
            
            results.append({
                'frames': frames,
                'policy': policy,
                'page_faults': manager.page_faults,
                'replacements': manager.replacements,
                'disk_writes': manager.disk_writes,
                'EAT': eat,
                'time_sec': elapsed
            })
            
            print(f"  Page Faults: {manager.page_faults:,}")
            print(f"  Reemplazos: {manager.replacements:,}")
            print(f"  Escrituras a disco: {manager.disk_writes:,}")
            print(f"  EAT: {eat:.2f} ns")
            print(f"  Tiempo ejecución: {elapsed:.2f} segundos")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Uso: python memory_simulator_large.py <archivo.trace>")
        return
    
    trace_file = sys.argv[1]
    
    # Configs Extra
    frame_counts = [10, 50, 100]
    replacement_policies = ['FIFO', 'LRU', 'OPT']
    
    # Process Trace File
    results = process_trace_file(trace_file, frame_counts, replacement_policies)
    
    # Mostrar tabla de resultados
    print("\nRESUMEN FINAL")
    print("="*80)
    print("Frames | Política | Page Faults | Reemplazos | Escrituras | EAT (ns)  | Tiempo (s)")
    print("-"*80)
    for res in results:
        print(f"{res['frames']:6} | {res['policy']:8} | {res['page_faults']:11,} | {res['replacements']:9,} | {res['disk_writes']:9,} | {res['EAT']:9.2f} | {res['time_sec']:9.2f}")

if __name__ == "__main__":
    main()

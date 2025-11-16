import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os
import time

class ElToqueTasaScraper:
    def __init__(self):
        self.url = "https://eltoque.com/tasas-de-cambio-de-moneda-en-cuba-hoy"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_eltoque(self):
        """Scraper específico para El Toque"""
        try:
            print("Conectando con El Toque...")
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar todas las tablas
            tables = soup.find_all('table')
            print(f"Se encontraron {len(tables)} tablas en la página")
            
            for i, table in enumerate(tables):
                print(f"Analizando tabla {i+1}...")
                # Buscar texto que indique que es la tabla de medianas
                table_text = table.get_text().lower()
                
                if any(keyword in table_text for keyword in ['mediana', 'compra', 'venta', 'usd', 'eur', 'mlc', 'moneda']):
                    print("¡Tabla de tasas encontrada!")
                    data = self.extract_table_data(table)
                    if data:
                        return data
            
            # Si no encuentra tabla, usar método alternativo
            print("Buscando datos con método alternativo...")
            return self.fallback_scrape(soup)
            
        except Exception as e:
            print(f"Error en el scraping: {e}")
            return None
    
    def extract_table_data(self, table):
        """Extrae datos de una tabla - solo compra, sin repetir monedas"""
        data = []
        monedas_encontradas = set()  # Para evitar duplicados
        rows = table.find_all('tr')
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:  # Solo necesitamos 2 columnas: moneda y compra
                row_data = [col.get_text(strip=True) for col in cols]
                print(f"Fila encontrada: {row_data}")
                
                # Verificar si es una fila de datos de moneda
                if self.is_currency_row(row_data):
                    # Normalizar el nombre de la moneda
                    moneda_normalizada = self.normalize_currency_name(row_data[0])
                    
                    # Solo tomar la columna de compra (generalmente la segunda columna)
                    compra_index = 1  # Índice de la columna de compra
                    
                    # Si hay encabezados, verificar cuál es la columna de compra
                    header_row = table.find('tr')
                    if header_row:
                        headers = [h.get_text(strip=True).lower() for h in header_row.find_all(['th', 'td'])]
                        if 'compra' in headers:
                            compra_index = headers.index('compra')
                    
                    # Verificar si ya tenemos esta moneda
                    if moneda_normalizada not in monedas_encontradas:
                        tasa = {
                            "moneda": moneda_normalizada,
                            "compra": self.clean_number(row_data[compra_index])
                        }
                        data.append(tasa)
                        monedas_encontradas.add(moneda_normalizada)
                        print(f"Datos extraídos: {tasa}")
                    else:
                        print(f"Moneda {moneda_normalizada} ya fue agregada, omitiendo...")
        
        return data
    
    def is_currency_row(self, row_data):
        """Verifica si una fila contiene datos de moneda"""
        currency_keywords = ['USD', 'EUR', 'MLC', 'CUP', 'EURO', 'DÓLAR', 'DOLAR', 'PESO', 'MONEDA LIBREMENTE CONVERTIBLE']
        
        # Verificar si la primera columna contiene alguna palabra clave de moneda
        first_col = row_data[0].upper()
        has_currency = any(keyword in first_col for keyword in currency_keywords)
        
        # Verificar si la columna de compra contiene números
        compra_index = 1  # Asumimos que compra es la segunda columna
        if len(row_data) > compra_index:
            has_numbers = any(char in row_data[compra_index] for char in '0123456789')
        else:
            has_numbers = False
        
        return has_currency and has_numbers
    
    def normalize_currency_name(self, currency_name):
        """Normaliza los nombres de las monedas"""
        name_upper = currency_name.upper()
        
        if 'USD' in name_upper or 'DÓLAR' in name_upper or 'DOLAR' in name_upper:
            return "USD"
        elif 'EUR' in name_upper or 'EURO' in name_upper:
            return "EUR"
        elif 'MLC' in name_upper or 'MONEDA LIBREMENTE CONVERTIBLE' in name_upper:
            return "MLC"
        elif 'CUP' in name_upper or 'PESO' in name_upper:
            return "CUP"
        else:
            return currency_name.strip()
    
    def fallback_scrape(self, soup):
        """Método alternativo si no encuentra tablas - solo compra, sin repetir"""
        data = []
        monedas_encontradas = set()
        content = soup.get_text()
        
        print("Buscando tasas de COMPRA en el texto de la página...")
        
        # Patrón para encontrar tasas de compra: Moneda seguida de un número (compra)
        patterns = [
            # USD - buscar solo compra
            (r'(USD|DÓLAR|DOLAR)[^\d]*([\d.,]+)', 'USD'),
            # EUR - buscar solo compra
            (r'(EUR|EURO)[^\d]*([\d.,]+)', 'EUR'),
            # MLC - buscar solo compra
            (r'(MLC|MONEDA LIBREMENTE CONVERTIBLE)[^\d]*([\d.,]+)', 'MLC'),
            # CUP - buscar solo compra
            (r'(CUP|PESO CUBANO)[^\d]*([\d.,]+)', 'CUP')
        ]
        
        for pattern, currency in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches and currency not in monedas_encontradas:
                # Tomar el primer número después del nombre de la moneda como compra
                data.append({
                    "moneda": currency,
                    "compra": self.clean_number(matches[0][1])
                })
                monedas_encontradas.add(currency)
                print(f"Datos COMPRA {currency} encontrados: {matches[0][1]}")
        
        # Si no encontramos datos, buscar cualquier patrón numérico que parezca tasas de compra
        if not data:
            data = self.deep_search(soup, monedas_encontradas)
        
        return data
    
    def deep_search(self, soup, monedas_encontradas):
        """Búsqueda más profunda en la página - solo compra, sin repetir"""
        data = []
        
        # Buscar en todos los textos que contengan números y palabras clave
        elements = soup.find_all(['p', 'div', 'span', 'li'])
        
        for element in elements:
            text = element.get_text().strip()
            if any(keyword in text.upper() for keyword in ['USD', 'EUR', 'MLC', 'COMPRA']):
                # Buscar patrones de números
                numbers = re.findall(r'(\d+[.,]?\d*)', text)
                if len(numbers) >= 1:  # Solo necesitamos al menos un número para compra
                    # Intentar determinar qué moneda es
                    if 'USD' in text.upper() or 'DÓLAR' in text.upper():
                        moneda = 'USD'
                    elif 'EUR' in text.upper() or 'EURO' in text.upper():
                        moneda = 'EUR'
                    elif 'MLC' in text.upper():
                        moneda = 'MLC'
                    else:
                        continue
                    
                    # Verificar si ya tenemos esta moneda
                    if moneda not in monedas_encontradas:
                        data.append({
                            "moneda": moneda,
                            "compra": self.clean_number(numbers[0])  # Primer número como compra
                        })
                        monedas_encontradas.add(moneda)
                        print(f"Datos COMPRA {moneda} encontrados en texto: {numbers[0]}")
        
        return data
    
    def clean_number(self, text):
        """Limpia y formatea números"""
        cleaned = re.sub(r'[^\d.,]', '', text)
        # Reemplazar coma por punto para formato numérico
        cleaned = cleaned.replace(',', '.')
        return cleaned
    
    def update_json(self):
        """Actualiza el archivo JSON en la misma carpeta"""
        print("Iniciando actualización de tasas de COMPRA...")
        new_data = self.scrape_eltoque()
        
        if not new_data:
            print("No se pudieron obtener datos de tasas de cambio")
            return False
        
        # Obtener la ruta actual donde se ejecuta el script
        current_directory = os.path.dirname(os.path.abspath(__file__))
        json_filename = "tasas_compra.json"
        json_path = os.path.join(current_directory, json_filename)
        
        # Estructura del JSON - solo compra
        output = {
            "ultima_actualizacion": datetime.now().isoformat(),
            "fuente": "El Toque",
            "url": self.url,
            "tasas_compra": new_data
        }
        
        # Guardar en archivo en la misma carpeta
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Datos de COMPRA actualizados correctamente en: {json_path}")
        print(f"📊 Tasas de COMPRA obtenidas (sin duplicados):")
        for tasa in new_data:
            print(f"   - {tasa['moneda']}: {tasa['compra']}")
        return True

def run_once():
    """Ejecuta el scraper una sola vez"""
    scraper = ElToqueTasaScraper()
    success = scraper.update_json()
    
    if success:
        print("✅ Scraping completado exitosamente")
    else:
        print("❌ Error en el scraping")

def run_scheduler():
    """Ejecuta el scraper periódicamente"""
    print("⏰ Iniciando scheduler de tasas de COMPRA...")
    print("🔄 El scraper se ejecutará cada hora")
    print("⏹️  Presiona Ctrl+C para detener")
    
    while True:
        try:
            # Ejecutar el scraper
            scraper = ElToqueTasaScraper()
            success = scraper.update_json()
            
            if success:
                print(f"✅ Scraping completado a las {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"❌ Error en scraping a las {datetime.now().strftime('%H:%M:%S')}")
            
            # Esperar 1 hora (3600 segundos) antes de la próxima ejecución
            print("⏳ Esperando 1 hora para la próxima actualización...")
            time.sleep(3600)
            
        except KeyboardInterrupt:
            print("\n🛑 Scheduler detenido por el usuario")
            break
        except Exception as e:
            print(f"❌ Error en scheduler: {e}")
            print("⏳ Reintentando en 1 hora...")
            time.sleep(3600)

if __name__ == "__main__":
    print("¿Cómo quieres ejecutar el scraper?")
    print("1 - Una sola vez")
    print("2 - En modo automático continuo (cada hora)")
    
    choice = input("Elige (1 o 2): ").strip()
    
    if choice == "1":
        run_once()
    elif choice == "2":
        run_scheduler()
    else:
        print("Opción no válida. Ejecutando una sola vez...")
        run_once()
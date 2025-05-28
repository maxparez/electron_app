#!/usr/bin/env python3
"""
Complete test of InvVzdProcessor with real files and date fixing
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'python'))

from tools.inv_vzd_processor import InvVzdProcessor

def test_complete_processing():
    """Test complete processing pipeline with real files"""
    print("=== Complete Processing Test ===")
    
    # Test with 16-hour data and template
    source_file = "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_ZŠ_2x.xlsx"
    template_file = "/root/vyvoj_sw/electron_app/legacy_code/inv/16_hodin_inovativniho_vzdelavani_sablona.xlsx"
    
    if os.path.exists(source_file) and os.path.exists(template_file):
        processor = InvVzdProcessor("16")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 Zdrojový soubor: {os.path.basename(source_file)}")
            print(f"📄 Šablona: {os.path.basename(template_file)}")
            print(f"📂 Výstupní složka: {temp_dir}")
            
            try:
                # Process the files
                result = processor.process_paths([source_file], template_file, temp_dir)
                
                print(f"\n🎯 Výsledek zpracování:")
                print(f"   Úspěch: {'✅' if result['success'] else '❌'}")
                
                # Show info messages (including date fixes)
                if processor.info_messages:
                    print(f"\n📋 Informace:")
                    for info in processor.info_messages:
                        print(f"   ℹ️ {info}")
                
                # Show warnings (including uncertain date fixes)
                if processor.warnings:
                    print(f"\n⚠️ Varování:")
                    for warning in processor.warnings:
                        print(f"   ⚠️ {warning}")
                
                # Show errors
                if processor.errors:
                    print(f"\n❌ Chyby:")
                    for error in processor.errors:
                        print(f"   ❌ {error}")
                
                # Show output files
                if result["output_files"]:
                    print(f"\n📁 Výstupní soubory:")
                    for output_file in result["output_files"]:
                        if os.path.exists(output_file):
                            filename = os.path.basename(output_file)
                            size = os.path.getsize(output_file)
                            print(f"   📄 {filename} ({size} bytů)")
                        else:
                            print(f"   ❌ {os.path.basename(output_file)} (neexistuje)")
                
                # Demonstrate UI-ready summary
                print(f"\n🎛️ UI Summary:")
                success_count = 1 if result["success"] else 0
                error_count = 1 if not result["success"] else 0
                print(f"   ✅ Úspěšně zpracováno: {success_count}")
                print(f"   ❌ S chybou: {error_count}")
                print(f"   📊 Celkem aktivit: {len(processor.info_messages) if hasattr(processor, 'hours_total') else 'N/A'}")
                print(f"   ⏱️ Celkem hodin: {getattr(processor, 'hours_total', 'N/A')}")
                        
            except Exception as e:
                print(f"❌ Neočekávaná chyba: {e}")
                import traceback
                traceback.print_exc()
    else:
        print("❌ Potřebné soubory nenalezeny pro test")

def show_ui_messages_example():
    """Show example of how UI messages would look"""
    print("\n=== Ukázka UI zpráv ===")
    
    # Simulate various scenarios
    scenarios = [
        {
            "file": "dochazka_MS_1_pololeti.xlsx",
            "status": "success",
            "messages": [
                ("info", "Detekována verze: 16 hodin"),
                ("info", "Doplněn rok 2024 pro datum 17.6. → 17.6.2024"),
                ("info", "Načteno 13 aktivit, celkem 22 hodin"),
                ("info", "Zpracování dokončeno úspěšně"),
            ],
            "output": "16h_inv_dochazka_MS_1_pololeti_MSMT.xlsx"
        },
        {
            "file": "dochazka_problematicka.xlsx", 
            "status": "warning",
            "messages": [
                ("info", "Detekována verze: 16 hodin"),
                ("warning", "Následující data byla opravena s nejistotou:"),
                ("warning", "  15.3. → 15.3.2024 (neistý)"),
                ("warning", "Zkontrolujte správnost a případně soubor opravte a spusťte znovu"),
                ("info", "Načteno 8 aktivit, celkem 16 hodin"),
            ],
            "output": "16h_inv_dochazka_problematicka_MSMT.xlsx"
        },
        {
            "file": "dochazka_chybna.xlsx",
            "status": "error", 
            "messages": [
                ("error", "Nesoulad verzí: zdrojový soubor má 32 hodin, ale šablona je pro 16 hodin"),
                ("warning", "Řešení: Vyberte šablonu pro 32 hodin nebo použijte 16hodinový zdrojový soubor"),
            ],
            "output": None
        }
    ]
    
    for scenario in scenarios:
        status_emoji = {"success": "✅", "warning": "⚠️", "error": "❌"}[scenario["status"]]
        print(f"\n📄 {scenario['file']} {status_emoji}")
        
        for msg_type, message in scenario["messages"]:
            emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}[msg_type]
            print(f"   {emoji} {message}")
            
        if scenario["output"]:
            print(f"   📁 Výstup: {scenario['output']}")

if __name__ == "__main__":
    test_complete_processing()
    show_ui_messages_example()
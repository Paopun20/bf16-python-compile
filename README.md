🚀 BF16 - Python Compiler  
🎮 Visual Brainfuck Runtime Engine

----------------------------------------

🔧 Requirements

🐍 Python 3.10 or later  
📦 Install dependencies:
    pip install -r requirements.txt

----------------------------------------

⚙️ Usage

🎨 RGB332 Mode:
    python bf16.py run examples/snake.b --color rgb332

🕶️ Grayscale Mode:
    python bf16.py run examples/badapple.b --color grayscale

----------------------------------------

🛠️ Compile BF16 Program

Convert `.b` source to `.bf16c` bytecode:

compile v1:
    python .\bf16.py compile .\examples\badapple.b

compile v2 (experimental, undone code and it can be corrupted file in the future):
    python .\bf16.py compile .\examples\badapple.b --use_v2_compile --color grayscale --appname "Bad Apple"

----------------------------------------

💡 Notes

.b = raw Brainfuck source  
.bf16c = compiled bytecode (v1/v2 supported)  
Supports color modes, event hooks (in code), and audio output
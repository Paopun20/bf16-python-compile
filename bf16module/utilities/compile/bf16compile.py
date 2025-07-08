import struct

class BF16compile:
    def __init__(self):
        self.program = []
        self.program_size = 0

    def compile(self, source: bytes) -> list[int]:
        self.program = []
        self.program_size = 0
        bracket_stack = []
        i = 0

        while i < len(source):
            ch = source[i]
            if ch in b'.?,[':
                self.program.append(ch)
                self.program.append(0)
                if ch == ord('['):
                    bracket_stack.append(len(self.program) - 2)
                self.program_size += 2
                i += 1
            elif ch in b'><+-':
                self.program.append(ch)
                count = 1
                j = i + 1
                while j < len(source) and source[j] == ch:
                    count += 1
                    j += 1
                self.program.append(count)
                self.program_size += 2
                i = j
            elif ch == ord(']'):
                self.program.append(ch)
                self.program.append(0)
                if bracket_stack:
                    open_idx = bracket_stack.pop()
                    close_idx = len(self.program) - 2
                    dist = close_idx - open_idx
                    self.program[open_idx + 1] = dist
                    self.program[close_idx + 1] = dist
                else:
                    print('Error: unmatched ] at byte', i)
                self.program_size += 2
                i += 1
            else:
                i += 1  # skip unrecognized characters/comments

        if bracket_stack:
            print('Error: unmatched [ at', bracket_stack)

        return self.program
    
    def _ReadBin(self, file):
        program = []
        while True:
            opcode_byte = file.read(1)
            if not opcode_byte:
                break
            opcode = struct.unpack('B', opcode_byte)[0]
            arg_bytes = file.read(2)
            if not arg_bytes:
                break
            arg = struct.unpack('<H', arg_bytes)[0]
            program.append(opcode)
            program.append(arg)
            program_size += 2
        return program

    def write_bin(self, filename: str):
        with open(filename, 'wb') as out:
            for idx in range(0, self.program_size, 2):
                opcode = self.program[idx]
                arg = self.program[idx + 1]
                out.write(struct.pack('B', opcode))
                out.write(struct.pack('<H', arg))

    def read_bin(self, filename: str):
        self.program_size = 0
        self.program = self._ReadBin(open(filename, 'rb'))
        return self.program
    
    def is_v2_bin(self, filename: str) -> bool:
        with open(filename, 'rb') as f:
            magic = f.read(4)
            if magic != b'BF16':
                return False
            version = struct.unpack('<B', f.read(1))[0]
            return version == 2 
    
    def write_bin_v2(self, filename: str, color_mode: str="rgb332", app_name: str="UNNAMED BF16"):
        with open(filename, 'wb') as f:
            # Write header
            f.write(b'BF16')  # Magic number
            f.write(struct.pack('<B', 2))  # Version (e.g., 2 for this new format)

            # Write metadata lengths
            f.write(struct.pack('<B', len(color_mode)))
            f.write(struct.pack('<B', len(app_name)))

            # Write metadata
            f.write(color_mode.encode('utf-8'))
            f.write(app_name.encode('utf-8'))

            # Write program
            for i in range(0, self.program_size, 2):
                f.write(struct.pack('<BH', self.program[i], self.program[i + 1]))
                
    def read_bin_v2(self, filename: str) -> tuple[list[int], str, str]:
        self.program = []
        self.program_size = 0
        color_mode = ""
        app_name = ""

        with open(filename, 'rb') as f:
            magic = f.read(4)
            if magic != b'BF16':
                raise ValueError("Invalid BF16 binary file (magic number mismatch)")

            version = struct.unpack('<B', f.read(1))[0]
            if version != 2:
                raise ValueError(f"Unsupported BF16 binary version: {version}. Expected 2.")

            color_mode_len = struct.unpack('<B', f.read(1))[0]
            app_name_len = struct.unpack('<B', f.read(1))[0]

            color_mode = f.read(color_mode_len).decode('utf-8')
            app_name = f.read(app_name_len).decode('utf-8')

            # For backup
            
            # while True:
            #     opcode_byte = f.read(1)
            #     if not opcode_byte:
            #         break
            #     opcode = struct.unpack('B', opcode_byte)[0]
            #     arg_bytes = f.read(2)
            #     if not arg_bytes:
            #         break
            #     arg = struct.unpack('<H', arg_bytes)[0]
            #     self.program.append(opcode)
            #     self.program.append(arg)
            #     self.program_size += 2
            self.program = self._ReadBin(f)
        return self.program, color_mode, app_name
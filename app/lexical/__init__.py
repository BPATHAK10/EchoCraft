"""
My custom lexical analyzer for my shell
"""

class MyLex:
    def __init__(self, input_text:str):
        self.input_text = input_text
        self.quoted = False
        self.double_quoted = False
        self.escape = False

        # Split the input into command and args
        spt = input_text.split(' ', 1)
        self.command = spt[0] if input_text else ''
        self.args = spt[1] if len(spt) > 1 else ''

        self.parsed_args = []


    def _process(self):
        # process the args
        arg = ''
        i = 0
        while i < len(self.args):
            char = self.args[i]
            if char == "\\" and not self.quoted and not self.double_quoted:
                self.escape = True
            elif self.escape:
                arg += char
                self.escape = False
                i += 1
                continue
            elif char == '"' and not self.double_quoted:
                self.double_quoted = True
                i += 1 
                continue               
            elif char == '"' and self.double_quoted:
                self.double_quoted = False
                self.parsed_args.append(arg)
                arg = ''
                i += 1
                continue
            elif char == "\\" and self.double_quoted:
                # Handle escaped characters in double quotes
                if i + 1 < len(self.args) and self.args[i + 1] == '"':
                    arg += '"'
                    i += 2
                    continue
                elif i + 1 < len(self.args) and self.args[i + 1] == '\\':
                    arg += "\\"
                    i += 2
                    continue
                else:
                    arg += "\\"
                    i += 1
                    continue

            elif char == "'" and not self.double_quoted:
                self.quoted = True
                i += 1
                continue

            elif char == "'" and self.quoted:
                self.quoted = False
                self.parsed_args.append(arg)
                arg = ''
                i += 1
                continue

            # build up the arg based upon the states
            if char == ' ' and not self.quoted and not self.double_quoted:            
                self.parsed_args.append(arg)
                arg = ''
                i += 1
            else:
                arg += char
                i += 1
        
        if arg:
            self.parsed_args.append(arg)


    def parse(self)-> list[str]:
        """
        Returns the comma separated of the command and args
        """

        self._process()
        
        return [self.command] + self.parsed_args
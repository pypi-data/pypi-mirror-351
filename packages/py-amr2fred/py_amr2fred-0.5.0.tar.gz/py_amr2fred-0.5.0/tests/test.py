from file_utilities import *
from amr2fred import Amr2fred, Glossary

amr2fred = Amr2fred()
n = 3
sentences = load_json("sentences.json")
rdf = {}
keys = list(sentences.keys())
for key in keys:
    text = sentences[key].get("text")
    print(text)
    rdf[text] = amr2fred.translate(text=text, serialize=True, mode=Glossary.RdflibMode.NT)
save_json("results.json", rdf)

import os
import subprocess
import tempfile
from pathlib import Path


class DigraphWriter:

    @staticmethod
    def node_to_digraph(root):
        """
        Returns root Node translated into .dot graphic language

        :param root: Node
        :return: str
        """
        # new_root = check_visibility(root)  # Uncomment if check_visibility is needed
        new_root = root

        digraph = Glossary.DIGRAPH_INI
        digraph += DigraphWriter.to_digraph(new_root)
        return digraph + Glossary.DIGRAPH_END

    @staticmethod
    def to_digraph(root):
        shape = "box"
        if root.is_malformed():
            shape = "ellipse"

        digraph = f'"{root.var}" [label="{root.var}", shape={shape},'
        if root.var.startswith(amr2fred.Glossary.FRED):
            digraph += ' color="0.5 0.3 0.5"];\n'
        else:
            digraph += ' color="1.0 0.3 0.7"];\n'

        if root.list and root.get_tree_status() == 0:
            for a in root.list:
                if a.visibility:
                    shape = "ellipse" if a.is_malformed() else "box"
                    digraph += f'"{a.var}" [label="{a.var}", shape={shape},'
                    if a.var.startswith(amr2fred.Glossary.FRED):
                        digraph += ' color="0.5 0.3 0.5"];\n'
                    else:
                        digraph += ' color="1.0 0.3 0.7"];\n'
                    if a.relation.lower() != Glossary.TOP.lower():
                        digraph += f'"{root.var}" -> "{a.var}" [label="{a.relation}"];\n'
                    digraph += DigraphWriter.to_digraph(a)

        return digraph

    @staticmethod
    def to_png(root):
        """
        Returns an image file (png) of the translated root node

        :param root: translated root node
        :return: image file (png)
        """
        tmp_out = None
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
            tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            tmp_out_path = Path(tmp_out.name)

            with open(tmp.name, 'w') as buff:
                buff.write(DigraphWriter.node_to_digraph(root))

            subprocess.run(f'dot -Tpng {tmp.name} -o {tmp_out.name}', shell=True, check=True)

            tmp_out_path.unlink(missing_ok=True)
            tmp_out_path.touch(exist_ok=True)

        except Exception as ex:
            print(f"Error: {ex}")

        return tmp_out

    @staticmethod
    def to_svg_string(root):
        """
        Return a String containing an SVG image of translated root node

        :param root: translated root node
        :return: str containing an SVG image
        """
        output = []

        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
            with open(tmp.name, 'w') as buff:
                buff.write(DigraphWriter.node_to_digraph(root))

            process = subprocess.Popen(f'dot -Tsvg {tmp.name}', shell=True, stdout=subprocess.PIPE, text=True)
            for line in process.stdout:
                output.append(line)

            process.wait()
            tmp.close()
            os.unlink(tmp.name)

        except Exception as ex:
            print(f"Error: {ex}")

        return ''.join(output)

    @staticmethod
    def check_visibility(root):
        for n in root.get_list():
            if not n.visibility:
                n.set_status(Node.REMOVE)

        root.list = [n for n in root.list if n.get_status() != Node.REMOVE]

        for n in root.get_list():
            DigraphWriter.check_visibility(n)

        return root


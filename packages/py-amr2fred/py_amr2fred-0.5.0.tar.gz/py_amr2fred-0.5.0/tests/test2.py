from pathlib import Path
import os


from file_utilities import *
from amr2fred import Amr2fred, Glossary


def test():
    amr2fred = Amr2fred()
    amr_text = """
        (c / charge-05 :ARG1 (h / he) :ARG2 (a / and :op1 (i / intoxicate-01 :ARG1 h :location (p / public))
        :op2 (r / resist-01 :ARG0 h :ARG1 (a2 / arrest-01 :ARG1 h))))
        """

    # AMR input in PENMAN format
    print(amr2fred.translate(amr=amr_text, serialize=True, mode=Glossary.RdflibMode.N3,
                             # alt_fred_ns="http://fred-01.org/domain.owl#"
                             ))
    #
    # # NL input text
    # print(amr2fred.translate(text="Apple unveils a revolutionary watch", serialize=True, mode=Glossary.RdflibMode.NT,
    #                          alt_api=False,
    #                          # alt_fred_ns="http://fred-01/domain.owl#"
    #                          ))

    # multilingual
    # print(amr2fred.translate(text="Quattro ragazzi preparano torte", serialize=True, mode=Glossary.RdflibMode.TURTLE,
    #                          alt_api=False,
    #                          multilingual=True,
    #                          # alt_fred_ns="http://fred-01/domain.owl#"
    #                          ))
    #
    # # PNG image output !!Attention!! Graphviz must be installed! The temporary file will not be automatically deleted
    # png_file = amr2fred.translate(text="Four boys making pies", serialize=True,
    #                               mode=Glossary.RdflibMode.NT,
    #                               alt_api=True,
    #                               graphic="png",
    #                               # alt_fred_ns="http://fred-01/domain.owl#"
    #                               )
    # save_path = "output_image.png"
    # if hasattr(png_file, "read"):
    #     with open(save_path, 'wb') as f:
    #         f.write(png_file.read())
    #     png_file.close()
    #     os.remove(Path(png_file.name))
    # else:
    #     print(png_file)
    #
    # # SVG image output !!Attention!! Graphviz must be installed!
    # svg = amr2fred.translate(text="Four boys making pies", serialize=True,
    #                          mode=Glossary.RdflibMode.NT,
    #                          alt_api=True,
    #                          graphic="svg",
    #                          # alt_fred_ns="http://fred-01/domain.owl#"
    #                          )
    #
    # save_path = "output_image.svg"
    # with open(save_path, 'w') as f:
    #     f.write(svg)


def test2():
    amr2fred = Amr2fred()
    amr = """(z0 / eat-01
        :ARG0 (z1 / person
                  :ARG0-of (z2 / kill-01))
        :ARG1 (z3 / pasta))"""

    svg = amr2fred.translate(amr=amr, text="The killer ate pasta",
                             # serialize=True,
                             # mode=Glossary.RdflibMode.NT,
                             # alt_api=True,
                             graphic="svg",
                             # alt_fred_ns="http://fred-01/domain.owl#"
                             )

    save_path = "output_image.svg"
    with open(save_path, 'w') as f:
        f.write(svg)

    amr = """(z0 / burn-01
        :ARG0 (z1 / car
                  :poss (z2 / person
                            :ARG0-of (z3 / kill-01)))
        :ARG1 (z4 / oil))"""
    svg = amr2fred.translate(amr=amr,
                             text=" The car of the killer burned oil.",
                             # serialize=True,
                             # mode=Glossary.RdflibMode.NT,
                             # alt_api=True,
                             graphic="svg",
                             # alt_fred_ns="http://fred-01/domain.owl#"
                             )

    save_path = "output_image2.svg"
    with open(save_path, 'w') as f:
        f.write(svg)

    png_file = amr2fred.translate(amr=amr,
                                  text=" The car of the killer burned oil.",
                                  serialize=True, mode=Glossary.RdflibMode.N3, graphic="png", post_processing=False
                                  # alt_fred_ns="http://fred-01.org/domain.owl#"
                                  )

    save_path = "output_image.png"
    if hasattr(png_file, "read"):
        with open(save_path, 'wb') as f:
            f.write(png_file.read())
        png_file.close()
        os.remove(Path(png_file.name))
    else:
        print(png_file)


def test3():

    amr2fred = Amr2fred()
    mode = Glossary.RdflibMode.N3
    amr_text = """ 
        (c / charge-05 :ARG1 (h / he) :ARG2 (a / and :op1 (i / intoxicate-01 :ARG1 h 
        :location (p / public)) :op2 (r / resist-01 :ARG0 h 
        :ARG1 (a2 / arrest-01 :ARG1 h)))) 
        """
    # translate from AMR

    print(amr2fred.translate(amr_text, serialize=True, mode=mode))

    mode = Glossary.RdflibMode.TURTLE

    print(amr2fred.translate(text="Four boys making pies", serialize=True, mode=mode))


def cont_text(amr_text, mode):
    amr2fred = Amr2fred()
    png_file = amr2fred.translate(amr=amr_text,
                                  # text=" The car of the killer burned oil.",
                                  # serialize=True, mode=Glossary.RdflibMode.N3,
                                  graphic="png", post_processing=False
                                  # alt_fred_ns="http://fred-01.org/domain.owl#"
                                  )
    save_path = "output_image.png"
    if hasattr(png_file, "read"):
        with open(save_path, 'wb') as f:
            f.write(png_file.read())
        png_file.close()
        os.remove(Path(png_file.name))
    else:
        print(png_file)


if __name__ == '__main__':
    amr = '''
    (z0 / count-01
    :mode imperative
    :ARG0 (z1 / you)
    :ARG1 (z2 / paper
              :topic (z3 / learn-01
                         :mod (z4 / deep))))
    '''
    cont_text(amr, "")
    test3()


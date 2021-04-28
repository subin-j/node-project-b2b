import logging


debugger = logging.getLogger("debugger")
f_hdlr = logging.FileHandler("./debugger.log")
s_hdlr = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
s_hdlr.setFormatter(formatter)
f_hdlr.setFormatter(formatter)

debugger.addHandler(f_hdlr)
debugger.addHandler(s_hdlr)
debugger.setLevel(logging.DEBUG)

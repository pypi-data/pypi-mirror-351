from .areas import *
import math

def rtotal(r1, r2, h1, h2, k, l, pi=math.pi):
    """
    calcula a troca de calor entre dois tubos cilíndricos concêntricos.
    :param r1: Raio interno do tubo 1.  
    :param r2: Raio externo do tubo 2.
    :hi é o coefficient de transferência de calor entre os tubos.
    :param k: Condutividade térmica do material do tubo.
    """
    a1 = areaSuperCilindro(r1, l)
    a2 = areaSuperCilindro(r2, l)
    rt = (1/(h1*a1) + math.log(r2/r1)/(2*pi*k*l) + 1/(h2*a2))
    return rt


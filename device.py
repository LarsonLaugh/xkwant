import kwant
import matplotlib.pyplot as plt
import numpy as np
from kwant import Builder, TranslationalSymmetry
from kwant.continuum import build_discretized,discretize_symbolic
from physics import *
from batch import *
from test import *


__all__ = ['Hbar']

class Hbar(Builder):
    def __init__(self,geo_params):
        super(Hbar,self).__init__()
        self.lx_leg = geo_params['lx_leg']
        self.ly_leg = geo_params['ly_leg']
        self.lx_neck = geo_params['lx_neck']
        self.ly_neck = geo_params['ly_neck']
        self.area = self.lx_leg*self.ly_leg*2+self.lx_neck*self.ly_neck
        self.ham_params = dict()
    def __str__(self):
        formatted_ham_params = ", ".join(f"{key}={value}" for key, value in self.ham_params.items())
        return (f"Instance of Hbar class:\n"
                f"Geometric parameters: lx_leg={self.lx_leg},ly_leg={self.ly_leg},lx_neck={self.lx_neck},ly_neck={self.ly_neck}\n"
                f"{len(self.leads)} leads have been attached\n"
                f"Hamitonian parameters: {formatted_ham_params}")
    def build_byfill(self,continuum_model):
        template = build_discretized(*discretize_symbolic(continuum_model))
        def hbar_shape(site):
            x,y = site.tag
            return ((0<=x<self.lx_leg and 0<=y<self.ly_leg) or (0<=x<self.lx_leg and
                                                               self.ly_leg+self.ly_neck<=y<self.ly_leg*2+self.ly_neck)
                    or (
                    self.lx_leg//2 - self.lx_neck//2 <=x< self.lx_leg//2 + self.lx_neck//2
                                                                                   and
                    self.ly_leg<=y<self.ly_leg+self.ly_neck))
        self.fill(template,hbar_shape,start=(0,0))
    def attach_lead_byfill(self,continuum_model,pos,conservation_law=None):
        template = build_discretized(*discretize_symbolic(continuum_model))
        if pos.upper() == 'BL':
            bot_left_lead = Builder(TranslationalSymmetry((-1,0)),conservation_law=conservation_law)
            bot_left_lead.fill(template,lambda site: 0 <= site.tag[1] <= self.ly_leg, (0, 1))
            self.attach_lead(bot_left_lead)
        elif pos.upper() == 'TL':
            top_left_lead = Builder(TranslationalSymmetry((-1,0)),conservation_law=conservation_law)
            top_left_lead.fill(template,lambda site: self.ly_leg+self.ly_neck <= site.tag[1] < self.ly_leg*2+self.ly_neck, (0,self.ly_leg+self.ly_neck))
            self.attach_lead(top_left_lead)
        elif pos.upper() == 'BR':
            bot_right_lead = Builder(TranslationalSymmetry((1,0)),conservation_law=conservation_law)
            bot_right_lead.fill(template,lambda site: 0 <= site.tag[1] <= self.ly_leg, (0,1))
            self.attach_lead(bot_right_lead)
        elif pos.upper() == 'TR':
            top_right_lead = Builder(TranslationalSymmetry((1,0)),conservation_law=conservation_law)
            top_right_lead.fill(template,lambda site: self.ly_leg+self.ly_neck <= site.tag[1] < self.ly_leg*2+self.ly_neck, (0,self.ly_leg+self.ly_neck))
            self.attach_lead(top_right_lead)
        else:
            raise ValueError(f"pos can only be BL, TL, BR, TR (case non-sensitive)")
    def set_ham_params(self,params):
        self.ham_params = params


if __name__ == '__main__':
    import cProfile

    # cProfile.run('test_hbar_from_cmodel()',sort='time')

    # cProfile.run('test_hbar_from_mk()',sort='time')

    test_batch()


    # fsyst = hbar_from_mk.finalized()

    # fig = plt.figure(figsize=(10,6),tight_layout=True)
    # ax1 = fig.add_subplot(121)
    # ax2 = fig.add_subplot(122)
    # kwant.plot(fsyst,ax=ax1)
    # kwant.plotter.bands(fsyst.leads[0],params=hbar_from_mk.ham_params,ax=ax2)

    # plt.show()




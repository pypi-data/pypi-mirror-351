'''
Date: 2024-08-15 19:54:22
LastEditors: BHM-Bob 2262029386@qq.com
LastEditTime: 2024-08-21 15:25:15
Description: print selected residue names and numbers as autodock flex receptor residue format
'''
import os
import tkinter as tk
import uuid
from typing import List

from nicegui import ui
from pymol import CmdException, api, cmd

from lazydock.pml.autodock_utils import MyFileDialog
from lazydock.utils import uuid4

NULL_CHAIN = "''"


def _get_res_info_from_sele(select: str, attrs: List[str] = None):
    """
    Parameters
    ----------
        - select : str, pymol selection
        - attrs : List[str], optional, attributes to get, by default ['model', 'chain', 'resn', 'resi']

    Returns
    -------
        - chains : dict
            - key: model_str:chain_str
            - value: dict
                - key: res_str:res_id_str
                - value: True
        - chains_data : dict
            - key: model_str
            - value: dict
                - key: chain_str
                - value: List[List[res_str, res_id]]
    """
    if attrs is None:
        attrs = ['model', 'chain', 'resn', 'resi']
    atoms = {k:[] for k in attrs}
    chains = {}
    chains_data = {}
    
    cmd.iterate(select, lambda atom: atoms.setdefault('model', []).append(atom.model))
    cmd.iterate(select, lambda atom: atoms.setdefault('chain', []).append(atom.chain))
    cmd.iterate(select, lambda atom: atoms.setdefault('resn', []).append(atom.resn))
    cmd.iterate(select, lambda atom: atoms.setdefault('resi', []).append(atom.resi))
    
    for m, c, r, i in zip(atoms['model'], atoms['chain'], atoms['resn'], atoms['resi']):
        chains.setdefault(f'{m}:{c}', {})[f'{r}{i}'] = True
        chains_data.setdefault(m, {c:[]})[c].append([r, i])
        
    return chains, chains_data
    

class LazyPocket:
    def __init__(self, app, _dev_mode: bool = False):
            
        self._app = app
        self._app.ui_update_func.append(self.ui_update_ui)
        
        self.ui_molecule = None
        self.ui_sele = None
        self.ui_radius = None
        
        self.sele = None
        self.sele_molecule = None
        self.sele_selection = None
        self.radius = None
        self.sele_chains = None
        
    def ui_update_ui(self):
        self.ui_molecule.set_options(self._app._now_molecule)
        self.ui_sele.set_options(self._app._now_selection)
        
    def build_flex_gui(self):
        # sele
        with ui.row().classes('w-full'):
            self.ui_molecule = ui.select(self._app._now_molecule,
                                          label = 'select a molecule').bind_value_to(self, 'sele_molecule').classes('w-1/5').props('use-chips')
            ui.label('OR')
            self.ui_sele = ui.select(self._app._now_selection,
                                     label = 'select a selection').bind_value_to(self, 'sele_selection').classes('w-1/5').props('use-chips')
        # radius
        self.ui_radius = ui.number(label = 'Radius (A)', min = 0, step=0.1, value = 0).bind_value_to(self, 'radius').classes('w-1/5')
        # buttons
        with ui.row().classes('w-full'):
            self.ui_print_butt = ui.button(text = 'print', on_click=self.print_sele_around_res)
            self.ui_save_butt = ui.button(text ='save rigid', on_click=self.save_rigid_receptor)
        # logs
        self.log = ui.log(max_lines=20).classes('w-full h-2/5')
        
    def build_gui(self):
        with ui.tabs().classes('w-full').props('align=left active-bg-color=blue') as tabs:
            self.ui_flex_tab = ui.tab('AutoDock Flex Residue Helper').props('no-caps')
        with ui.tab_panels(tabs, value=self.ui_flex_tab).classes('w-full'):
            with ui.tab_panel(self.ui_flex_tab):
                self.build_flex_gui()
        # return self
        return self
        
    def print_sele_around_res(self):
        """output example: CB1:D:PHE108_PHE177_HIS178_LEU193_PHE379_SER383"""
        self.sele = self.sele_molecule or self.sele_selection
        if self.radius:
            pocket = f'Pocket_{uuid4()}'
            if self.sele_molecule:
                cmd.select(pocket, f'model {self.sele_molecule}')
                cmd.select(pocket, f'byres {pocket} around {self.radius}')
            else:
                cmd.select(pocket, f'byres {self.sele} around {self.radius}')
            self.sele = pocket
        chains, self.sele_chains = _get_res_info_from_sele(self.sele)
        final_output = ",".join(f"{k}:{'_'.join(v.keys())}" for k,v in chains.items())
        log = f'Residue names and numbers as autodock flex receptor residue format:\n{final_output}'
        print(log)
        self.log.push(log)
        
    def save_rigid_receptor(self):
        if self.sele_chains is None:
            ui.notify('Please run "Print sele (around pocket) in flex residue format" first.')
            return None
        pdb_path = MyFileDialog(types = [('PDB file', '*.pdb')],
                                initialdir=os.getcwd()).get_save_file()
        if pdb_path is None:
            ui.notify('Please choose a file to save.')
            return None
        if not pdb_path.endswith('.pdb'):
            pdb_path += '.pdb'
        is_first = True
        for model in self.sele_chains:
            tmp_model_name = f'{model}_{str(uuid.uuid4())[:4]}'
            api.copy(tmp_model_name, model)
            for chain in self.sele_chains[model]:
                for _, resi in self.sele_chains[model][chain]:
                    tmp_sele_name = f'{tmp_model_name}_{chain}_{resi}'
                    try:
                        api.select(tmp_sele_name, f'model {tmp_model_name} and (chain {chain or NULL_CHAIN} and resi {resi})')
                    except CmdException:
                        # TODO: don't kown why, but copy again helps
                        api.copy(tmp_model_name, model)
                        api.select(tmp_sele_name, f'model {tmp_model_name} and (chain {chain or NULL_CHAIN} and resi {resi})')
                    cmd.remove(tmp_sele_name)
                    cmd.delete(tmp_sele_name)
            api.multisave(pdb_path, tmp_model_name, append = 0 if is_first else 1)
            is_first = False
        log = f'Rigid receptor saved to {pdb_path}.'
        print(log)
        self.log.push(log)
            
        
# dev mode
if __name__ in {"__main__", "__mp_main__"}:    
    cmd.reinitialize()
    cmd.load('data_tmp/pdb/LIGAND.pdb', 'ligand')
    cmd.load('data_tmp/pdb/RECEPTOR.pdb', 'receptor')
    
    from main import GUILauncher
    GUILauncher()
    
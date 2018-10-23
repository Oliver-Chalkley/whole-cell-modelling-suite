# Author: Oliver Chalkley
# Affiliation: Bristol Centre for Complexity Science (BCCS) and the Bristol Minimal Genome Group (MGG)
# Date of creation: 06/12/2017

# import relavent libraries
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.cluster import adjusted_rand_score
from sklearn.cluster import DBSCAN
from scipy.cluster import hierarchy as hc
import sys
from py2cytoscape.data.cynetwork import CyNetwork
from py2cytoscape.data.cyrest_client import CyRestClient
from py2cytoscape.data.style import StyleUtil
import py2cytoscape.util.cytoscapejs as cyjs
import py2cytoscape.cytoscapejs as renderer

import networkx as nx
import pandas as pd
import json
from pathlib import Path
import socket
home = str(Path.home())
hostname = socket.gethostname()
if hostname == 'it050032.users.bris.ac.uk':
	home = '/space/oc13378/myprojects/github/uob'
else:
	home = home + '/git/uob'

path_from_home_to_wcming_suite = 'wc/mg/oc2/whole_cell_modelling_suite'
print('path = ', home + '/' + path_from_home_to_wcming_suite)
sys.path.insert(0, home + '/' + path_from_home_to_wcming_suite)
from connections import Bc3
import cytoscape
from cytoscape import CytoscapeNetworkConnection

class MGS():
    def __init__(self, name_to_ko_set_codes_dict = None):
        if name_to_ko_set_codes_dict == None:
            self.name_to_ko_set_codes_dict = self.getHistoricalMGSs()
        else:
            self.name_to_ko_set_codes_dict = name_to_ko_set_codes_dict
        # create bc3 connection in order to access the staticDB which is the official source of our codes and IDs etc
        self.db_conn = Bc3('oc13378', 'bc3', '/users/oc13378/.ssh/uob/uob-rsa', 'Oliver', 'Chalkley', 'o.chalkley@bristol.ac.uk')

#        self.all_codes = self.getAllGeneCodes() # removed cause I ended up resorting to the official static.db data
        self.ko_code_to_id_dict = self.getDictOfJr358Codes()
        self.ko_id_to_code_dict = self.createIdToCodeDict()
        self.idx_to_id_dict = self.createIdxToIdDict(self.ko_code_to_id_dict)
        self.id_to_idx_dict = self.invertDictionary(self.idx_to_id_dict)
        self.genomes = self.convertKoListsToGenomes()

    def getHistoricalMGSs(self):
        """Returns a dictionary that contains allthe published minimal gene sets collected by Chalkley and Rees."""
        # removed MG_025 and MG_469 from here as crashy
        dict_of_MGS_predictions = {'Koonin_1': ['MG_007','MG_014','MG_020','MG_022','MG_027','MG_029','MG_031','MG_034','MG_037','MG_039','MG_040','MG_041','MG_046','MG_051','MG_055','MG_473','MG_061','MG_062','MG_064','MG_069','MG_075','MG_084','MG_085','MG_098','MG_099','MG_100','MG_101','MG_476','MG_105','MG_109','MG_110','MG_121','MG_123','MG_128','MG_130','MG_132','MG_137','MG_139','MG_149','MG_179','MG_181','MG_183','MG_184','MG_186','MG_188','MG_189','MG_190','MG_191','MG_192','MG_200','MG_205','MG_208','MG_481','MG_482','MG_213','MG_214','MG_217','MG_218','MG_225','MG_226','MG_230','MG_235','MG_236','MG_240','MG_264','MG_277','MG_288','MG_289','MG_290','MG_291','MG_298','MG_302','MG_303','MG_304','MG_309','MG_310','MG_311','MG_312','MG_315','MG_316','MG_317','MG_318','MG_321','MG_323','MG_324','MG_327','MG_329','MG_517','MG_342','MG_344','MG_349','MG_352','MG_356','MG_368','MG_369','MG_370','MG_372','MG_376','MG_385','MG_386','MG_390','MG_396','MG_409','MG_412','MG_419','MG_427','MG_428','MG_429','MG_438','MG_442','MG_447','MG_454','MG_460','MG_464','MG_467','MG_468','MG_526','MG_470'], 'Hutchinson_1': ['MG_009','MG_014','MG_029','MG_033','MG_049','MG_051','MG_052','MG_062','MG_085','MG_110','MG_130','MG_132','MG_149','MG_182','MG_183','MG_186','MG_191','MG_192','MG_209','MG_213','MG_226','MG_264','MG_288','MG_291','MG_293','MG_295','MG_310','MG_316','MG_317','MG_327','MG_335','MG_339','MG_345','MG_346','MG_352','MG_370','MG_372','MG_380','MG_385','MG_390','MG_394','MG_408','MG_410','MG_411','MG_412','MG_421','MG_426','MG_428','MG_438','MG_442','MG_467','MG_468','MG_470'], 'Tomita_1': ['MG_001','MG_003','MG_004','MG_006','MG_007','MG_008','MG_009','MG_012','MG_013','MG_014','MG_015','MG_019','MG_020','MG_022','MG_026','MG_027','MG_029','MG_030','MG_031','MG_034','MG_037','MG_039','MG_040','MG_042','MG_043','MG_044','MG_045','MG_046','MG_047','MG_048','MG_049','MG_050','MG_051','MG_052','MG_053','MG_055','MG_058','MG_059','MG_061','MG_062','MG_063','MG_064','MG_065','MG_066','MG_071','MG_072','MG_073','MG_075','MG_077','MG_078','MG_079','MG_080','MG_083','MG_084','MG_085','MG_086','MG_091','MG_094','MG_097','MG_098','MG_099','MG_100','MG_101','MG_102','MG_104','MG_105','MG_106','MG_107','MG_109','MG_110','MG_112','MG_118','MG_119','MG_120','MG_121','MG_122','MG_123','MG_124','MG_127','MG_128','MG_130','MG_132','MG_137','MG_139','MG_141','MG_143','MG_145','MG_149','MG_169','MG_170','MG_171','MG_172','MG_179','MG_180','MG_181','MG_182','MG_183','MG_184','MG_186','MG_187','MG_188','MG_189','MG_190','MG_191','MG_192','MG_195','MG_200','MG_201','MG_203','MG_204','MG_205','MG_206','MG_208','MG_209','MG_210','MG_212','MG_213','MG_214','MG_217','MG_218','MG_221','MG_224','MG_225','MG_226','MG_227','MG_228','MG_229','MG_230','MG_231','MG_235','MG_236','MG_238','MG_239','MG_240','MG_244','MG_245','MG_250','MG_252','MG_254','MG_258','MG_259','MG_261','MG_262','MG_264','MG_265','MG_270','MG_271','MG_272','MG_273','MG_274','MG_275','MG_276','MG_277','MG_278','MG_282','MG_287','MG_288','MG_289','MG_290','MG_291','MG_293','MG_295','MG_297','MG_298','MG_299','MG_302','MG_303','MG_304','MG_305','MG_309','MG_310','MG_312','MG_315','MG_316','MG_317','MG_318','MG_321','MG_322','MG_323','MG_324','MG_327','MG_329','MG_330','MG_333','MG_335','MG_336','MG_339','MG_342','MG_346','MG_347','MG_349','MG_352','MG_353','MG_355','MG_356','MG_357','MG_358','MG_359','MG_367','MG_368','MG_369','MG_370','MG_372','MG_376','MG_379','MG_380','MG_382','MG_383','MG_384','MG_385','MG_386','MG_387','MG_390','MG_391','MG_392','MG_393','MG_394','MG_396','MG_398','MG_399','MG_400','MG_401','MG_402','MG_403','MG_404','MG_405','MG_408','MG_409','MG_410','MG_411','MG_412','MG_419','MG_421','MG_425','MG_427','MG_428','MG_434','MG_435','MG_438','MG_442','MG_445','MG_447','MG_448','MG_453','MG_454','MG_457','MG_458','MG_463','MG_464','MG_465','MG_467','MG_468','MG_470','MG_473','MG_476','MG_481','MG_482','MG_498','MG_517','MG_526'], 'Gil_2004_1': ['MG_012','MG_013','MG_014','MG_015','MG_020','MG_022','MG_027','MG_029','MG_033','MG_034','MG_037','MG_038','MG_039','MG_040','MG_042','MG_043','MG_044','MG_045','MG_049','MG_050','MG_051','MG_052','MG_053','MG_061','MG_062','MG_063','MG_064','MG_065','MG_071','MG_073','MG_075','MG_077','MG_078','MG_079','MG_080','MG_085','MG_086','MG_098','MG_099','MG_100','MG_101','MG_104','MG_105','MG_106','MG_109','MG_110','MG_114','MG_118','MG_119','MG_120','MG_121','MG_122','MG_123','MG_127','MG_128','MG_130','MG_137','MG_139','MG_149','MG_179','MG_180','MG_181','MG_182','MG_183','MG_184','MG_186','MG_187','MG_188','MG_189','MG_190','MG_191','MG_192','MG_200','MG_203','MG_204','MG_205','MG_206','MG_208','MG_209','MG_210','MG_213','MG_214','MG_217','MG_218','MG_221','MG_225','MG_226','MG_230','MG_236','MG_238','MG_239','MG_240','MG_244','MG_245','MG_252','MG_265','MG_270','MG_271','MG_272','MG_273','MG_274','MG_275','MG_276','MG_277','MG_278','MG_287','MG_288','MG_289','MG_290','MG_291','MG_293','MG_298','MG_299','MG_302','MG_303','MG_304','MG_309','MG_310','MG_312','MG_316','MG_317','MG_318','MG_321','MG_322','MG_323','MG_324','MG_327','MG_330','MG_333','MG_335','MG_339','MG_342','MG_344','MG_347','MG_349','MG_352','MG_355','MG_356','MG_357','MG_358','MG_359','MG_365','MG_368','MG_369','MG_370','MG_372','MG_376','MG_380','MG_382','MG_383','MG_385','MG_386','MG_390','MG_408','MG_409','MG_410','MG_411','MG_412','MG_419','MG_421','MG_427','MG_428','MG_434','MG_438','MG_442','MG_445','MG_447','MG_448','MG_453','MG_454','MG_467','MG_468','MG_470','MG_473','MG_476','MG_481','MG_482','MG_498','MG_517','MG_526'], 'Glass_1': ['MG_009','MG_012','MG_033','MG_039','MG_040','MG_051','MG_061','MG_062','MG_063','MG_066','MG_110','MG_112','MG_114','MG_121','MG_149','MG_183','MG_210','MG_213','MG_214','MG_226','MG_227','MG_238','MG_244','MG_252','MG_264','MG_271','MG_288','MG_289','MG_290','MG_291','MG_293','MG_298','MG_315','MG_316','MG_339','MG_346','MG_352','MG_355','MG_358','MG_359','MG_367','MG_370','MG_380','MG_385','MG_390','MG_398','MG_408','MG_410','MG_411','MG_412','MG_428','MG_437','MG_438','MG_454','MG_460','MG_463','MG_498'], 'Church_1': ['MG_001','MG_003','MG_004','MG_006','MG_007','MG_008','MG_009','MG_012','MG_013','MG_014','MG_015','MG_019','MG_020','MG_022','MG_023','MG_027','MG_029','MG_030','MG_031','MG_033','MG_034','MG_037','MG_038','MG_039','MG_040','MG_041','MG_042','MG_043','MG_044','MG_045','MG_046','MG_047','MG_048','MG_049','MG_050','MG_051','MG_052','MG_053','MG_055','MG_058','MG_059','MG_061','MG_062','MG_063','MG_064','MG_065','MG_066','MG_069','MG_071','MG_072','MG_073','MG_075','MG_077','MG_078','MG_079','MG_080','MG_083','MG_084','MG_085','MG_086','MG_091','MG_094','MG_097','MG_098','MG_101','MG_102','MG_104','MG_105','MG_106','MG_107','MG_109','MG_110','MG_111','MG_112','MG_114','MG_118','MG_119','MG_120','MG_121','MG_122','MG_123','MG_124','MG_127','MG_128','MG_130','MG_132','MG_137','MG_139','MG_141','MG_143','MG_145','MG_149','MG_170','MG_172','MG_177','MG_179','MG_180','MG_181','MG_182','MG_183','MG_184','MG_186','MG_187','MG_188','MG_189','MG_190','MG_191','MG_192','MG_200','MG_201','MG_203','MG_204','MG_205','MG_206','MG_208','MG_209','MG_210','MG_212','MG_213','MG_214','MG_215','MG_216','MG_217','MG_218','MG_221','MG_224','MG_225','MG_226','MG_227','MG_228','MG_229','MG_230','MG_231','MG_235','MG_236','MG_238','MG_239','MG_240','MG_244','MG_245','MG_249','MG_250','MG_252','MG_254','MG_261','MG_262','MG_264','MG_265','MG_270','MG_271','MG_272','MG_273','MG_274','MG_275','MG_276','MG_277','MG_278','MG_282','MG_287','MG_288','MG_289','MG_290','MG_291','MG_293','MG_295','MG_297','MG_298','MG_299','MG_300','MG_301','MG_302','MG_303','MG_304','MG_305','MG_309','MG_310','MG_312','MG_315','MG_316','MG_317','MG_318','MG_321','MG_322','MG_323','MG_324','MG_327','MG_329','MG_330','MG_333','MG_335','MG_336','MG_339','MG_340','MG_341','MG_342','MG_344','MG_346','MG_347','MG_349','MG_352','MG_353','MG_355','MG_356','MG_357','MG_358','MG_359','MG_367','MG_368','MG_369','MG_370','MG_372','MG_376','MG_379','MG_380','MG_382','MG_383','MG_384','MG_385','MG_386','MG_387','MG_390','MG_391','MG_394','MG_396','MG_398','MG_399','MG_400','MG_401','MG_402','MG_403','MG_404','MG_405','MG_407','MG_408','MG_409','MG_410','MG_411','MG_412','MG_419','MG_421','MG_425','MG_427','MG_428','MG_429','MG_430','MG_431','MG_434','MG_437','MG_438','MG_442','MG_447','MG_448','MG_453','MG_454','MG_457','MG_458','MG_460','MG_463','MG_464','MG_467','MG_468','MG_470','MG_473','MG_476','MG_481','MG_482','MG_498','MG_517','MG_526'], 'Atlas_1': ['MG_012','MG_013','MG_014','MG_015','MG_020','MG_022','MG_027','MG_029','MG_033','MG_034','MG_037','MG_038','MG_039','MG_040','MG_042','MG_043','MG_044','MG_045','MG_049','MG_050','MG_051','MG_052','MG_053','MG_061','MG_062','MG_063','MG_064','MG_065','MG_071','MG_073','MG_075','MG_077','MG_078','MG_079','MG_080','MG_085','MG_086','MG_098','MG_099','MG_100','MG_101','MG_104','MG_105','MG_106','MG_109','MG_110','MG_114','MG_118','MG_119','MG_120','MG_121','MG_122','MG_123','MG_127','MG_128','MG_130','MG_132','MG_137','MG_139','MG_149','MG_179','MG_180','MG_181','MG_182','MG_183','MG_184','MG_186','MG_187','MG_188','MG_189','MG_190','MG_191','MG_192','MG_200','MG_203','MG_204','MG_205','MG_206','MG_208','MG_209','MG_210','MG_213','MG_214','MG_217','MG_218','MG_221','MG_225','MG_226','MG_230','MG_236','MG_238','MG_239','MG_240','MG_244','MG_245','MG_252','MG_265','MG_270','MG_271','MG_272','MG_273','MG_274','MG_275','MG_276','MG_277','MG_278','MG_287','MG_288','MG_289','MG_290','MG_291','MG_293','MG_298','MG_299','MG_302','MG_303','MG_304','MG_309','MG_310','MG_312','MG_316','MG_317','MG_318','MG_321','MG_322','MG_323','MG_324','MG_327','MG_330','MG_333','MG_335','MG_339','MG_342','MG_344','MG_347','MG_349','MG_352','MG_355','MG_356','MG_357','MG_358','MG_359','MG_365','MG_368','MG_369','MG_370','MG_372','MG_376','MG_380','MG_382','MG_383','MG_385','MG_386','MG_390','MG_391','MG_408','MG_409','MG_410','MG_411','MG_412','MG_419','MG_421','MG_427','MG_428','MG_434','MG_438','MG_442','MG_445','MG_447','MG_448','MG_453','MG_454','MG_467','MG_468','MG_470','MG_473','MG_476','MG_481','MG_482','MG_498','MG_517','MG_526'], 'Huang_1': ['MG_006','MG_007','MG_009','MG_012','MG_013','MG_014','MG_015','MG_020','MG_022','MG_023','MG_026','MG_027','MG_029','MG_030','MG_031','MG_033','MG_034','MG_037','MG_038','MG_039','MG_040','MG_041','MG_042','MG_043','MG_044','MG_045','MG_049','MG_050','MG_051','MG_052','MG_053','MG_055','MG_061','MG_062','MG_063','MG_064','MG_065','MG_069','MG_071','MG_073','MG_075','MG_077','MG_078','MG_079','MG_080','MG_085','MG_086','MG_090','MG_091','MG_093','MG_097','MG_098','MG_099','MG_100','MG_101','MG_104','MG_105','MG_106','MG_109','MG_110','MG_114','MG_118','MG_119','MG_120','MG_121','MG_122','MG_123','MG_127','MG_128','MG_130','MG_132','MG_137','MG_139','MG_143','MG_149','MG_153','MG_159','MG_164','MG_169','MG_174','MG_179','MG_180','MG_181','MG_182','MG_183','MG_184','MG_186','MG_187','MG_188','MG_189','MG_190','MG_191','MG_192','MG_197','MG_200','MG_201','MG_203','MG_204','MG_205','MG_206','MG_208','MG_209','MG_210','MG_212','MG_213','MG_214','MG_215','MG_216','MG_217','MG_218','MG_221','MG_225','MG_226','MG_227','MG_228','MG_229','MG_230','MG_232','MG_235','MG_236','MG_238','MG_239','MG_240','MG_244','MG_245','MG_251','MG_252','MG_259','MG_264','MG_265','MG_270','MG_271','MG_272','MG_273','MG_274','MG_275','MG_276','MG_277','MG_278','MG_283','MG_287','MG_288','MG_289','MG_290','MG_291','MG_293','MG_298','MG_299','MG_302','MG_303','MG_304','MG_309','MG_310','MG_312','MG_315','MG_316','MG_317','MG_318','MG_321','MG_322','MG_323','MG_324','MG_325','MG_327','MG_330','MG_333','MG_335','MG_336','MG_339','MG_342','MG_344','MG_346','MG_347','MG_349','MG_351','MG_352','MG_353','MG_355','MG_356','MG_357','MG_358','MG_359','MG_363','MG_365','MG_368','MG_369','MG_370','MG_372','MG_375','MG_376','MG_379','MG_380','MG_382','MG_383','MG_385','MG_386','MG_387','MG_390','MG_391','MG_393','MG_396','MG_398','MG_402','MG_403','MG_404','MG_405','MG_408','MG_409','MG_410','MG_411','MG_412','MG_419','MG_421','MG_426','MG_427','MG_428','MG_430','MG_434','MG_437','MG_438','MG_442','MG_447','MG_448','MG_453','MG_454','MG_458','MG_460','MG_464','MG_465','MG_466','MG_467','MG_468','MG_470','MG_473','MG_476','MG_481','MG_482','MG_498','MG_517','MG_522','MG_526'], 'Karr_1': ['MG_009','MG_014','MG_015','MG_027','MG_029','MG_030','MG_033','MG_039','MG_040','MG_050','MG_052','MG_055','MG_059','MG_061','MG_062','MG_063','MG_064','MG_065','MG_073','MG_075','MG_083','MG_085','MG_086','MG_097','MG_101','MG_105','MG_119','MG_120','MG_121','MG_123','MG_127','MG_130','MG_132','MG_149','MG_186','MG_187','MG_188','MG_189','MG_190','MG_200','MG_203','MG_205','MG_206','MG_209','MG_482','MG_213','MG_214','MG_225','MG_226','MG_227','MG_235','MG_236','MG_240','MG_244','MG_250','MG_252','MG_259','MG_262','MG_498','MG_264','MG_265','MG_288','MG_289','MG_290','MG_291','MG_293','MG_298','MG_309','MG_310','MG_315','MG_316','MG_324','MG_327','MG_333','MG_336','MG_339','MG_344','MG_346','MG_349','MG_352','MG_353','MG_355','MG_356','MG_358','MG_359','MG_369','MG_370','MG_376','MG_380','MG_385','MG_390','MG_398','MG_399','MG_400','MG_401','MG_402','MG_403','MG_404','MG_405','MG_408','MG_409','MG_410','MG_411','MG_412','MG_421','MG_427','MG_428','MG_438','MG_447','MG_448','MG_454','MG_457','MG_460','MG_463','MG_467','MG_468','MG_526','MG_470'], 'Gil_2014_1': ['MG_009','MG_012','MG_013','MG_014','MG_015','MG_020','MG_022','MG_027','MG_029','MG_033','MG_034','MG_037','MG_038','MG_039','MG_040','MG_042','MG_043','MG_044','MG_045','MG_049','MG_050','MG_051','MG_052','MG_053','MG_061','MG_062','MG_063','MG_064','MG_065','MG_071','MG_073','MG_075','MG_077','MG_078','MG_079','MG_080','MG_085','MG_086','MG_091','MG_098','MG_099','MG_100','MG_101','MG_104','MG_105','MG_106','MG_109','MG_110','MG_114','MG_118','MG_119','MG_120','MG_121','MG_122','MG_123','MG_127','MG_128','MG_130','MG_132','MG_137','MG_139','MG_149','MG_179','MG_180','MG_181','MG_182','MG_183','MG_184','MG_186','MG_187','MG_188','MG_189','MG_190','MG_191','MG_192','MG_200','MG_203','MG_204','MG_205','MG_206','MG_208','MG_209','MG_210','MG_213','MG_214','MG_217','MG_218','MG_221','MG_225','MG_226','MG_230','MG_236','MG_238','MG_239','MG_240','MG_244','MG_245','MG_252','MG_265','MG_270','MG_271','MG_272','MG_273','MG_274','MG_275','MG_276','MG_277','MG_278','MG_287','MG_288','MG_289','MG_290','MG_291','MG_293','MG_298','MG_299','MG_302','MG_303','MG_304','MG_309','MG_310','MG_312','MG_316','MG_317','MG_318','MG_321','MG_322','MG_323','MG_324','MG_327','MG_330','MG_333','MG_335','MG_339','MG_342','MG_344','MG_347','MG_349','MG_352','MG_355','MG_356','MG_357','MG_358','MG_359','MG_365','MG_368','MG_369','MG_370','MG_372','MG_376','MG_380','MG_382','MG_383','MG_385','MG_386','MG_390','MG_408','MG_409','MG_410','MG_411','MG_412','MG_419','MG_421','MG_427','MG_428','MG_434','MG_438','MG_442','MG_445','MG_447','MG_448','MG_453','MG_454','MG_460','MG_467','MG_468','MG_470','MG_473','MG_476','MG_481','MG_482','MG_498','MG_517','MG_526'], 'Agreed_1': ['MG_009','MG_033','MG_039','MG_040','MG_061','MG_062','MG_063','MG_121','MG_149','MG_213','MG_214','MG_226','MG_227','MG_244','MG_252','MG_498','MG_264','MG_288','MG_289','MG_290','MG_291','MG_293','MG_298','MG_315','MG_316','MG_339','MG_346','MG_352','MG_355','MG_358','MG_359','MG_370','MG_380','MG_385','MG_390','MG_398','MG_408','MG_410','MG_411','MG_412','MG_428','MG_438','MG_454','MG_460','MG_463']}

        return dict_of_MGS_predictions

# initial investigation tools

    def createAriDistanceMatrix(self):
        """Takes a dictionary of KO sets and returns a distance (or similarity) matrix which is basically how many genes do they have in common."""
        genomes_df = self.genomes.copy()
        ino_of_genes, no_of_genomes = genomes_df.shape
        distance_matrix = np.empty((no_of_genomes, no_of_genomes,))
        distance_matrix[:] = np.NAN
        for col_idx in range(no_of_genomes):
            for row_idx in range(no_of_genomes):
                distance_matrix[row_idx, col_idx] = 1 - adjusted_rand_score(genomes_df[genomes_df.columns[row_idx]], genomes_df[genomes_df.columns[col_idx]])

        return distance_matrix

    def sumeriseEssentialityByGene(self):
        """This function compares all the genomes in the instance and categorises each gene as universally essential, universally non-essential or transient."""
        # find out the amount and size of genomes we're dealing with
        size_of_genome, no_of_genomes = self.genomes.shape
        # get gene codes for universally non-essential genes
        universal_ne_codes_tuple = tuple(self.genomes.index[(self.genomes.sum(axis=1) == 0)])
        # get gene codes for universally essential genes
        universal_e_codes_tuple = tuple(self.genomes.index[(self.genomes.sum(axis=1) == no_of_genomes)])
        # get gene codes for universally essential genes
        transient_codes_tuple = tuple(self.genomes.index[( (self.genomes.sum(axis=1) > 0) & (self.genomes.sum(axis=1) < 123) )])

        # create output dict
        output_dict = {'universal_essential_codes': universal_e_codes_tuple, 'universal_non_essential_codes': universal_ne_codes_tuple, 'transient_codes': transient_codes_tuple}

        return output_dict

    def getGeneCodesBySimilarityClassification(self, genome1, genome2, name_of_genome1, name_of_genome2):
        """This function takes two genomes and returns a dictionary of classification to gene codes where the classifications are agreed KIs, agreed KOs, genome1/2 specific KIs, and genome1/2 specific KOs."""
        agreed_ki_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] == genome2[idx] and genome1[idx] == 1)])
        agreed_ko_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] == genome2[idx] and genome1[idx] == 0)])
        genome1_ki_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] != genome2[idx] and genome1[idx] == 1)])
        genome2_ki_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] != genome2[idx] and genome2[idx] == 1)])
        genome1_ko_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] != genome2[idx] and genome1[idx] == 0)])
        genome2_ko_idx = tuple([idx for idx in range(len(genome1)) if (genome1[idx] != genome2[idx] and genome2[idx] == 0)])
        # convert into codes and put into a dict
        names = ('agreed_kis', 'agreed_kos', name_of_genome1 + '_kis', name_of_genome2 + '_kis', name_of_genome1 + '_kos', name_of_genome2 + '_kos')
        output_dict = {'agreed_kis': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in agreed_ki_idx]), 'agreed_kos': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in agreed_ko_idx]), name_of_genome1 + '_specific_kis': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in genome1_ki_idx]), name_of_genome2 + '_specific_kis': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in genome2_ki_idx]), name_of_genome1 + '_specific_kos': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in genome1_ko_idx]), name_of_genome2 + '_specific_kos': tuple([self.ko_id_to_code_dict[self.idx_to_id_dict[idx]] for idx in genome2_ko_idx])}

        return output_dict

    def createSimilarityMatrix(self, similarity_function, array_of_genomes = None):
        """
        Takes an array of genomes and calculates a similarity matrix which is the proportion of genome they have in common.
        
        array_of_genomes is an nxm np array where n is the number of genomes and m is the number of genes.
        """
        if array_of_genomes == None:
            array_of_genomes = self.genomes

        total_genomes, total_genes = array_of_genomes.shape
        similarity_matrix = np.empty((total_genomes, total_genomes,))
        similarity_matrix[:] = np.nan
        for genome1_idx in range(total_genomes):
            for genome2_idx in range(total_genomes):
                similarity_matrix[genome1_idx, genome2_idx] = similarity_function(array_of_genomes[genome1_idx, :], array_of_genomes[genome2_idx, :])


        return similarity_matrix

    @staticmethod
    def getSimpleSimilarity(genome1, genome2):
        if len(genome1) != len(genome2):
            raise ValueError('Genome1 and genome2 must have the same length!')

        is_gene_correct = [1 if genome1[idx] == genome2[idx] else 0 for idx in range(len(genome1))]

        return sum(is_gene_correct)/(len(is_gene_correct) * 1.0)

    def createDistanceMatrix(self):
        """Takes a dictionary of KO sets and returns a distance (or similarity) matrix which is basically how many genes do they have in common."""
        dict_of_ko_sets = self.name_to_ko_set_codes_dict.copy()
        no_of_ko_sets = len(dict_of_ko_sets.keys())
        distance_matrix = np.empty((no_of_ko_sets, no_of_ko_sets,))
        distance_matrix[:] = np.NAN
        list_of_ko_set_keys = list(dict_of_ko_sets.keys())
        for col_idx in range(len(list_of_ko_set_keys)):
            for row_idx in range(len(list_of_ko_set_keys)):
                tmp_set1 = set(dict_of_ko_sets[list_of_ko_set_keys[row_idx]])
                tmp_set2 = set(dict_of_ko_sets[list_of_ko_set_keys[col_idx]])
                len1 = len(tmp_set1)
                len2 = len(tmp_set2)
                # in order for this to work with the clustering libraries the distance matrix has to be symetric (or anti-symetric??). This won't be the case if we divide by the leading genome length, so in order to make a valid distance matrix we divide by the larger of the two KO sets.
                largest_length = len1
                if len2 > len1:
                    largest_length = len2

                # NEED TO CHANGE THIS BECAUSE THE NUMBER OF GENES IN COMMON CAN BE VERY DIFFERENT FROM THE NUMBER OF GENES THAT ARE DIFFERENT. PLUS IF WE DO THE GENES IN COMMON WE CAN DIVIDE BY THE LENGTH OF THE WT GENOME WHICH MAKES MORE SENSE THAN THE ABOVE SOLUTION TO GETTING A SYMMETRIC DISTANCE MATRIX
                no_common_genes = len(tmp_set1.intersection(tmp_set2))
                distance_matrix[row_idx, col_idx] = largest_length - no_common_genes

        return distance_matrix

    def plotDendogramOfMGSs(self, distance_matrix, filename = None, legend_labels = None):
        dist_matrix_condensed = hc.distance.squareform(distance_matrix)
        z = hc.linkage(dist_matrix_condensed, method='average')
        dendrogram = hc.dendrogram(z)
        if legend_labels is not None:
            plt.legend(legend_labels)

        if filename is None:
            plt.show()
        else:
            plt.savefig(filename, bbox_inches='tight')

        return 

    def convertKoListsToGenomes(self, name_to_ko_set_codes_dict = None):
        no_of_genes = len(self.ko_code_to_id_dict)
        if name_to_ko_set_codes_dict == None:
            ko_sets = self.name_to_ko_set_codes_dict.copy()
        else:
            ko_sets = name_to_ko_set_codes_dict.copy()

        wt_genome = [1]*no_of_genes
        genomes = [float('NaN') for i in range(len(ko_sets))]
        idx_to_id_dict = self.idx_to_id_dict.copy()
        id_to_idx_dict = self.id_to_idx_dict.copy()
        ko_set_names = list(ko_sets.keys())
        for ko_set_idx in range(len(ko_sets)):
            tmp_genome = wt_genome.copy()
            for gene_code in ko_sets[ko_set_names[ko_set_idx]]:
                ids = self.ko_code_to_id_dict[gene_code]
                idx = id_to_idx_dict[ids]
                tmp_genome[idx] = 0

            genomes[ko_set_idx] = tmp_genome

        genomes = np.array(genomes)
        genomes = np.transpose(genomes)
        # we want the pandas dataframe index to be gene codes and so we need to go from the genome index to the gene ID to the gene code
        list_of_ordered_gene_codes = [self.ko_id_to_code_dict[idx_to_id_dict[idx]] for idx in range(len(tmp_genome))]
        genomes = pd.DataFrame(genomes, columns=ko_set_names, index=list_of_ordered_gene_codes)

        return genomes

    def plotGenomes(self, array_of_genomes, plot_save_name = None):
        if plot_save_name == None:
            plt.pcolor(array_of_genomes.T)
            plt.colorbar()
            plt.show()
        else:
            fig1 = plt.figure(1)
            plt.pcolor(array_of_genomes.T)
            plt.colorbar()
            plt.savefig(plot_save_name)

        return

    def orderGeneomesWithDbscan(self, distance_matrix):
        # calculate the average distance for DBSCAN
        genomes = self.genomes.copy()
        average_distance = distance_matrix.mean()
        min_group_size = 1
        db = DBSCAN(eps = average_distance, min_samples = min_group_size, metric="precomputed")
        db.fit_predict(distance_matrix)
        clust_groups = db.labels_
        max_group = max(clust_groups)

        # create empty array for reordered genomes
        genomes_reordered = np.empty(genomes.shape)
        genomes_reordered[:] = np.NAN
        counter = 0
        for group in range(max_group + 1):
            group_idxs = [i for i, j in enumerate(clust_groups) if j == group]
            for idx in group_idxs:
                genomes_reordered[counter, :] = genomes[idx, :]
                counter += 1

        return genomes_reordered

# CYTOSCAPE TOOLS
    def deleteAllNetworksInCytoscape(self):
        cytoscape.CytoscapeCommunicationFunctions.deleteAllNetworksInCytoscape('http://localhost:1234/v1/')

    def loadRelatedKeggMaps(self, tuple_of_genes):
        cyto_input = 'u'
        while not (cyto_input.lower() == 'y' or cyto_input.lower() == 'n'):
            cyto_input = input("In order to create KEGG maps in Cytoscape, Cytoscape needs to be connected to localhost on port 1234. Is this true? (y/n): ")
                
        if cyto_input.lower() == 'n':
            print("Cytoscape must be connected to local host through port 1234. Exiting...")
            return

        # get all relavent kegg data
        kegg_dir, xml_file_names, gene_code_to_kegg_id_dicts, kegg_style_tuple_of_dirs = self.getRelatedKeggMapPaths(tuple_of_genes)

        # create cytoscape connections
        cytoscape_conns = {tmp_xml[:-4]: CytoscapeNetworkConnection(CytoscapeNetworkConnection.loadFromKeggFile, {'absolute_path_to_file': kegg_dir + '/' + tmp_xml}, delete_all_cytoscape_networks = False) for tmp_xml in xml_file_names}

        return cytoscape_conns, gene_code_to_kegg_id_dicts, kegg_style_tuple_of_dirs

    def save_all_networks_in_cytoscape_as_image(self, file_format = 'pdf'):
        cytoscape.hjk

    def highlightGenesOnKegg(self, dict_of_cytoscape_conns, gene_code_to_kegg_id_dicts, tuple_of_genes, new_node_colour = 'red'):
        # highlight all relavent genes 
        # create dict of desired node properties
        node_property_dict = {'NODE_FILL_COLOR': new_node_colour}
        change_node_resp_dict = {}
        for kegg_id in dict_of_cytoscape_conns.keys():
            # get kegg_id_to_node_idx_dict
            kegg_gene_id_to_node_idx_dict = dict_of_cytoscape_conns[kegg_id].getKeggIdToNodeIdx()
            # change node properties for all related genes in this pathway map
#            for gene_code in gene_code_to_kegg_id_dicts['kegg_to_gene'][kegg_id[3:]]:
            change_node_resp_dict = {}
            for gene_code in gene_code_to_kegg_id_dicts['kegg_to_gene'][kegg_id[3:]]:
                if tuple_of_genes.count(gene_code) > 0:
                    for node_idx in kegg_gene_id_to_node_idx_dict['mge:' + gene_code]:
                        change_node_resp_dict[kegg_id] = {gene_code: {node_idx: dict_of_cytoscape_conns[kegg_id].changeNodeAttribute(node_idx, node_property_dict)}}
                        time.sleep(5)
#            change_node_resp_dict[kegg_id] = {gene_code: {node_idx: dict_of_cytoscape_conns[kegg_id].changeNodeAttribute(node_idx, node_property_dict) for node_idx in kegg_gene_id_to_node_idx_dict['mge:' + gene_code]} for gene_code in gene_code_to_kegg_id_dicts['kegg_to_gene'][kegg_id[3:]] if tuple_of_genes.count(gene_code) > 0}
            print("change_node_resp_dict = ", change_node_resp_dict)


    def getKeggInfoDf(self, tuple_of_genes):
        # get relationship beween gene codes and kegg ids
        kegg_ids, gene_codes = self.getKeggToGeneLists()
        kegg_dict = self.getKeggData()
        # create a dataframe of nans
        kegg_info_df = pd.DataFrame(columns=kegg_dict, index=tuple_of_genes)
        for kegg_idx in range(len(kegg_dict['code'])):
            for gene_code in tuple_of_genes:
                if gene_code in kegg_dict['allAssociatedGeneCodes'][kegg_idx]:
                    kegg_info_df.loc[gene_code, kegg_dict['category'][kegg_idx]] = True
                else:
                    kegg_info_df.loc[gene_code, kegg_dict['category'][kegg_idx]] = False

        return kegg_info_df

    def getKeggData(self):
        # Ontology_KEGG_14.06.2016
        kegg_dict_mg_37 = {}
        kegg_dict_mg_37['code'] = ['mge00010', 'mge00020', 'mge00030', 'mge00040', 'mge00051', 'mge00052', 'mge00190', 'mge00230', 'mge00240', 'mge00260', 'mge00270', 'mge00280', 'mge00430', 'mge00450', 'mge00480', 'mge00500', 'mge00520', 'mge00561', 'mge00564', 'mge00620', 'mge00630', 'mge00640', 'mge00670', 'mge00680', 'mge00740', 'mge00760', 'mge00770', 'mge00790', 'mge00970', 'mge02010', 'mge02020', 'mge02060', 'mge03010', 'mge03018', 'mge03020', 'mge03030', 'mge03060', 'mge03070', 'mge03410', 'mge03420', 'mge03430', 'mge03440', 'mge04122']
        kegg_dict_mg_37['level'] = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        kegg_dict_mg_37['category'] = ['Glycolysis / Gluconeogenesis', 'Citrate cycle (TCA cycle)', 'Pentose phosphate pathway', 'Pentose and glucuronate interconversions', 'Fructose and mannose metabolism', 'Galactose metabolism', 'Oxidative phosphorylation', 'Purine metabolism', 'Pyrimidine metabolism', 'Glycine, serine and threonine metabolism', 'Cysteine and methionine metabolism', 'Valine, leucine and isoleucine degradation', 'Taurine and hypotaurine metabolism', 'Selenocompound metabolism', 'Glutathione metabolism', 'Starch and sucrose metabolism', 'Amino sugar and nucleotide sugar metabolism', 'Glycerolipid metabolism', 'Glycerophospholipid metabolism', 'Pyruvate metabolism', 'Glyoxylate and dicarboxylate metabolism', 'Propanoate metabolism', 'One carbon pool by folate', 'Methane metabolism', 'Riboflavin metabolism', 'Nicotinate and nicotinamide metabolism', 'Pantothenate and CoA biosynthesis', 'Folate biosynthesis', 'Aminoacyl-tRNA biosynthesis', 'ABC transporters', 'Two-component system', 'Phosphotransferase system (PTS)', 'Ribosome', 'RNA degradation', 'RNA polymerase', 'DNA replication', 'Protein export', 'Bacterial secretion system', 'Base excision repair', 'Nucleotide excision repair', 'Mismatch repair', 'Homologous recombination', 'Sulfur relay system']
        kegg_dict_mg_37['allAssociatedGeneCodes'] = [['MG_023', 'MG_069', 'MG_111', 'MG_215', 'MG_216', 'MG_271', 'MG_272', 'MG_273', 'MG_274', 'MG_300', 'MG_301', 'MG_407', 'MG_430', 'MG_431', 'MG_460'], ['MG_271', 'MG_272', 'MG_273', 'MG_274'], ['MG_023', 'MG_050', 'MG_058', 'MG_066', 'MG_111', 'MG_112', 'MG_215', 'MG_396'], ['MG_112', 'MG_453'], ['MG_023', 'MG_053', 'MG_062', 'MG_063', 'MG_215', 'MG_396', 'MG_431'], ['MG_118', 'MG_137', 'MG_215', 'MG_453'], ['MG_351', 'MG_398', 'MG_399', 'MG_400', 'MG_401', 'MG_402', 'MG_403', 'MG_404', 'MG_405'], ['MG_001', 'MG_007', 'MG_022', 'MG_031', 'MG_049', 'MG_058', 'MG_107', 'MG_171', 'MG_177', 'MG_216', 'MG_229', 'MG_231', 'MG_261', 'MG_262', 'MG_276', 'MG_315', 'MG_340', 'MG_341', 'MG_419', 'MG_458'], ['MG_001', 'MG_006', 'MG_007', 'MG_022', 'MG_030', 'MG_031', 'MG_034', 'MG_049', 'MG_051', 'MG_052', 'MG_102', 'MG_177', 'MG_227', 'MG_229', 'MG_231', 'MG_261', 'MG_262', 'MG_315', 'MG_330', 'MG_340', 'MG_341', 'MG_382', 'MG_419', 'MG_434'], ['MG_271', 'MG_394', 'MG_430'], ['MG_047', 'MG_460'], ['MG_271'], ['MG_299', 'MG_357'], ['MG_021', 'MG_102', 'MG_336'], ['MG_391'], ['MG_069', 'MG_111', 'MG_453'], ['MG_053', 'MG_069', 'MG_111', 'MG_118', 'MG_137', 'MG_453'], ['MG_038', 'MG_212', 'MG_247', 'MG_368', 'MG_517'], ['MG_039', 'MG_114', 'MG_212', 'MG_247', 'MG_293', 'MG_368', 'MG_385', 'MG_437'], ['MG_216', 'MG_271', 'MG_272', 'MG_273', 'MG_274', 'MG_299', 'MG_357', 'MG_460'], ['MG_271', 'MG_394'], ['MG_271', 'MG_299', 'MG_357', 'MG_460'], ['MG_013', 'MG_227', 'MG_228', 'MG_245', 'MG_365', 'MG_394'], ['MG_023', 'MG_215', 'MG_299', 'MG_357', 'MG_394', 'MG_407', 'MG_430'], ['MG_145'], ['MG_037', 'MG_049', 'MG_115', 'MG_128', 'MG_240', 'MG_383'], ['MG_264', 'MG_482'], ['MG_228'], ['MG_005', 'MG_021', 'MG_035', 'MG_036', 'MG_099', 'MG_100', 'MG_113', 'MG_126', 'MG_136', 'MG_194', 'MG_195', 'MG_251', 'MG_253', 'MG_266', 'MG_283', 'MG_292', 'MG_334', 'MG_345', 'MG_365', 'MG_375', 'MG_378', 'MG_455', 'MG_462', 'MG_471', 'MG_472', 'MG_475', 'MG_479', 'MG_483', 'MG_484', 'MG_485', 'MG_486', 'MG_487', 'MG_488', 'MG_489', 'MG_490', 'MG_492', 'MG_493', 'MG_495', 'MG_496', 'MG_497', 'MG_499', 'MG_500', 'MG_501', 'MG_502', 'MG_503', 'MG_504', 'MG_506', 'MG_507', 'MG_508', 'MG_509', 'MG_510', 'MG_511', 'MG_512', 'MG_513', 'MG_514', 'MG_518', 'MG_519', 'MG_520', 'MG_523'], ['MG_042', 'MG_043', 'MG_044', 'MG_045', 'MG_077', 'MG_078', 'MG_079', 'MG_080', 'MG_179', 'MG_180', 'MG_181', 'MG_187', 'MG_289', 'MG_290', 'MG_291', 'MG_302', 'MG_303', 'MG_304', 'MG_410', 'MG_411', 'MG_412'], ['MG_412', 'MG_469'], ['MG_062', 'MG_069', 'MG_429'], ['MG_070', 'MG_081', 'MG_082', 'MG_087', 'MG_088', 'MG_090', 'MG_092', 'MG_093', 'MG_150', 'MG_151', 'MG_152', 'MG_153', 'MG_154', 'MG_155', 'MG_156', 'MG_157', 'MG_158', 'MG_159', 'MG_160', 'MG_161', 'MG_162', 'MG_163', 'MG_164', 'MG_165', 'MG_166', 'MG_167', 'MG_168', 'MG_169', 'MG_174', 'MG_175', 'MG_176', 'MG_178', 'MG_197', 'MG_198', 'MG_232', 'MG_234', 'MG_257', 'MG_311', 'MG_325', 'MG_361', 'MG_362', 'MG_363', 'MG_417', 'MG_418', 'MG_424', 'MG_426', 'MG_444', 'MG_446', 'MG_466', 'MG_473', 'MG_481', 'MG_522', 'MG_rrnA16S', 'MG_rrnA23S', 'MG_rrnA5S'], ['MG_104', 'MG_130', 'MG_139', 'MG_215', 'MG_305', 'MG_392', 'MG_407', 'MG_423'], ['MG_022', 'MG_177', 'MG_340', 'MG_341'], ['MG_001', 'MG_007', 'MG_010', 'MG_031', 'MG_091', 'MG_094', 'MG_250', 'MG_254', 'MG_261', 'MG_262', 'MG_315', 'MG_419'], ['MG_0001', 'MG_048', 'MG_055', 'MG_072', 'MG_170', 'MG_210', 'MG_277', 'MG_297', 'MG_464', 'MG_476'], ['MG_048', 'MG_055', 'MG_072', 'MG_170', 'MG_277', 'MG_297', 'MG_464', 'MG_476'], ['MG_097', 'MG_235', 'MG_254', 'MG_262', 'MG_498'], ['MG_073', 'MG_206', 'MG_244', 'MG_254', 'MG_262', 'MG_421'], ['MG_001', 'MG_007', 'MG_031', 'MG_091', 'MG_244', 'MG_254', 'MG_261', 'MG_315', 'MG_419'], ['MG_001', 'MG_007', 'MG_031', 'MG_091', 'MG_261', 'MG_262', 'MG_315', 'MG_339', 'MG_358', 'MG_359', 'MG_419'], ['MG_295', 'MG_372']]
        return kegg_dict_mg_37

    def getRelatedKeggMapPaths(self, tuple_of_genes):

        # gene codes for the kegg map references don't ever NOT have underscores after MG however some do in Karrs. I checked that if Karr has a code without an underscore then there isn't an equivalent one with an underscore because of this we can just put underscores in where they're missing:
        tuple_of_genes = tuple([code if code[2] == "_" else code[:2] + '_' + code[2:] for code in tuple_of_genes])
        # get relationship beween gene codes and kegg ids
        kegg_ids, gene_codes = self.getKeggToGeneLists()

        # create two one to many dictionaries
        # get unique ids
        unique_kegg_ids = list(set(kegg_ids))
        unique_gene_codes = list(set(gene_codes))
        # create both dictionaries
        kegg_to_gene_codes_dict = {kegg_id: list(set([gene_codes[i] for i, j in enumerate(kegg_ids) if j == kegg_id])) for kegg_id in unique_kegg_ids}
        gene_to_kegg_codes_dict = {gene_code: list(set([kegg_ids[i] for i, j in enumerate(gene_codes) if j == gene_code])) for gene_code in unique_gene_codes}
        gene_code_to_kegg_id_dicts = {'gene_to_kegg': gene_to_kegg_codes_dict, 'kegg_to_gene': kegg_to_gene_codes_dict}

        # create list of all the kegg ids neccessary
        used_kegg_ids = []
        for gene_code in tuple_of_genes:
            tmp_list = [kegg_ids[idx] for idx in range(len(kegg_ids)) if gene_codes[idx] == gene_code]
            used_kegg_ids = used_kegg_ids + tmp_list

        # turn list into unique list
        used_kegg_ids = list(set(used_kegg_ids))
        KEGG_DIR = "/home/oli/Dropbox/Documents/PhD/gene_ontology/kegg/kegg_pathway_xmls"
        pathways = ['mge' + kegg_id + '.xml' for kegg_id in used_kegg_ids]
#        pathways = ['mge00010.xml', 'mge00020.xml', 'mge00030.xml', 'mge00040.xml', 'mge00051.xml', 'mge00052.xml', 'mge00190.xml', 'mge00230.xml', 'mge00240.xml', 'mge00260.xml', 'mge00270.xml', 'mge00280.xml', 'mge00430.xml', 'mge00450.xml', 'mge00480.xml', 'mge00500.xml', 'mge00520.xml', 'mge00561.xml', 'mge00564.xml', 'mge00620.xml', 'mge00630.xml', 'mge00640.xml', 'mge00670.xml', 'mge00680.xml', 'mge00730.xml', 'mge00740.xml', 'mge00760.xml', 'mge00770.xml', 'mge00790.xml', 'mge00970.xml', 'mge01100.xml', 'mge01110.xml', 'mge01120.xml', 'mge01130.xml', 'mge01200.xml', 'mge01230.xml', 'mge02010.xml', 'mge02020.xml', 'mge02024.xml', 'mge02060.xml', 'mge03010.xml', 'mge03018.xml', 'mge03020.xml', 'mge03030.xml', 'mge03060.xml', 'mge03070.xml', 'mge03410.xml', 'mge03420.xml', 'mge03430.xml', 'mge03440.xml', 'mge04122.xml']

#        # Step 1: Create py2cytoscape client
#        cy = CyRestClient()
#
#
#        # Reset
#        cy.session.delete()
#
#        # Step 2: Load network from somewhere
#        for pathway in pathways:
#            mg_net = cy.network.create_from(KEGG_DIR + '/' + pathway)
        return KEGG_DIR, pathways, gene_code_to_kegg_id_dicts, tuple_of_genes

    def getKeggToGeneLists(self):
        """
        This returns two lists. (1) kegg IDs (this is a repeating list!) (2) gene codes (also repeating list!!).

        The lists have repeating elements because they have a many to many relationship and kegg_id[x] corresponding to gene_code[x].
        """
        kegg_id_to_gene_code = [('00010', 'MG_023'), ('00010', 'MG_069'), ('00010', 'MG_111'), ('00010', 'MG_215'), ('00010', 'MG_216'), ('00010', 'MG_271'), ('00010', 'MG_272'), ('00010', 'MG_273'), ('00010', 'MG_274'), ('00010', 'MG_300'), ('00010', 'MG_301'), ('00010', 'MG_407'), ('00010', 'MG_430'), ('00010', 'MG_431'), ('00010', 'MG_460'), ('00020', 'MG_271'), ('00020', 'MG_272'), ('00020', 'MG_273'), ('00020', 'MG_274'), ('00030', 'MG_023'), ('00030', 'MG_050'), ('00030', 'MG_058'), ('00030', 'MG_066'), ('00030', 'MG_111'), ('00030', 'MG_112'), ('00030', 'MG_215'), ('00030', 'MG_396'), ('00040', 'MG_112'), ('00040', 'MG_453'), ('00051', 'MG_023'), ('00051', 'MG_053'), ('00051', 'MG_062'), ('00051', 'MG_063'), ('00051', 'MG_215'), ('00051', 'MG_396'), ('00051', 'MG_431'), ('00052', 'MG_118'), ('00052', 'MG_137'), ('00052', 'MG_215'), ('00052', 'MG_453'), ('00190', 'MG_351'), ('00190', 'MG_398'), ('00190', 'MG_399'), ('00190', 'MG_400'), ('00190', 'MG_401'), ('00190', 'MG_402'), ('00190', 'MG_403'), ('00190', 'MG_404'), ('00190', 'MG_405'), ('00230', 'MG_001'), ('00230', 'MG_007'), ('00230', 'MG_022'), ('00230', 'MG_031'), ('00230', 'MG_049'), ('00230', 'MG_058'), ('00230', 'MG_107'), ('00230', 'MG_171'), ('00230', 'MG_177'), ('00230', 'MG_216'), ('00230', 'MG_229'), ('00230', 'MG_231'), ('00230', 'MG_261'), ('00230', 'MG_262'), ('00230', 'MG_276'), ('00230', 'MG_315'), ('00230', 'MG_340'), ('00230', 'MG_341'), ('00230', 'MG_419'), ('00230', 'MG_458'), ('00240', 'MG_001'), ('00240', 'MG_006'), ('00240', 'MG_007'), ('00240', 'MG_022'), ('00240', 'MG_030'), ('00240', 'MG_031'), ('00240', 'MG_034'), ('00240', 'MG_049'), ('00240', 'MG_051'), ('00240', 'MG_052'), ('00240', 'MG_177'), ('00240', 'MG_227'), ('00240', 'MG_229'), ('00240', 'MG_231'), ('00240', 'MG_261'), ('00240', 'MG_262'), ('00240', 'MG_315'), ('00240', 'MG_330'), ('00240', 'MG_340'), ('00240', 'MG_341'), ('00240', 'MG_382'), ('00240', 'MG_419'), ('00240', 'MG_434'), ('00260', 'MG_271'), ('00260', 'MG_394'), ('00260', 'MG_430'), ('00270', 'MG_047'), ('00270', 'MG_460'), ('00280', 'MG_271'), ('00430', 'MG_299'), ('00430', 'MG_357'), ('00450', 'MG_021'), ('00450', 'MG_102'), ('00450', 'MG_336'), ('00480', 'MG_391'), ('00500', 'MG_069'), ('00500', 'MG_111'), ('00500', 'MG_453'), ('00520', 'MG_053'), ('00520', 'MG_069'), ('00520', 'MG_111'), ('00520', 'MG_118'), ('00520', 'MG_137'), ('00520', 'MG_453'), ('00561', 'MG_038'), ('00561', 'MG_212'), ('00561', 'MG_247'), ('00561', 'MG_368'), ('00561', 'MG_517'), ('00564', 'MG_039'), ('00564', 'MG_114'), ('00564', 'MG_212'), ('00564', 'MG_247'), ('00564', 'MG_293'), ('00564', 'MG_368'), ('00564', 'MG_385'), ('00564', 'MG_437'), ('00620', 'MG_216'), ('00620', 'MG_271'), ('00620', 'MG_272'), ('00620', 'MG_273'), ('00620', 'MG_274'), ('00620', 'MG_299'), ('00620', 'MG_357'), ('00620', 'MG_460'), ('00630', 'MG_271'), ('00630', 'MG_394'), ('00640', 'MG_271'), ('00640', 'MG_299'), ('00640', 'MG_357'), ('00640', 'MG_460'), ('00670', 'MG_013'), ('00670', 'MG_227'), ('00670', 'MG_228'), ('00670', 'MG_245'), ('00670', 'MG_365'), ('00670', 'MG_394'), ('00680', 'MG_023'), ('00680', 'MG_215'), ('00680', 'MG_299'), ('00680', 'MG_357'), ('00680', 'MG_394'), ('00680', 'MG_407'), ('00680', 'MG_430'), ('00730', 'MG_110'), ('00730', 'MG_171'), ('00730', 'MG_372'), ('00740', 'MG_145'), ('00760', 'MG_037'), ('00760', 'MG_049'), ('00760', 'MG_115'), ('00760', 'MG_128'), ('00760', 'MG_240'), ('00760', 'MG_383'), ('00770', 'MG_264'), ('00770', 'MG_482'), ('00790', 'MG_228'), ('00970', 'MG_005'), ('00970', 'MG_021'), ('00970', 'MG_035'), ('00970', 'MG_036'), ('00970', 'MG_099'), ('00970', 'MG_100'), ('00970', 'MG_113'), ('00970', 'MG_126'), ('00970', 'MG_136'), ('00970', 'MG_194'), ('00970', 'MG_195'), ('00970', 'MG_251'), ('00970', 'MG_253'), ('00970', 'MG_266'), ('00970', 'MG_283'), ('00970', 'MG_292'), ('00970', 'MG_334'), ('00970', 'MG_345'), ('00970', 'MG_365'), ('00970', 'MG_375'), ('00970', 'MG_378'), ('00970', 'MG_455'), ('00970', 'MG_462'), ('00970', 'MG_471'), ('00970', 'MG_472'), ('00970', 'MG_475'), ('00970', 'MG_479'), ('00970', 'MG_483'), ('00970', 'MG_484'), ('00970', 'MG_485'), ('00970', 'MG_486'), ('00970', 'MG_487'), ('00970', 'MG_488'), ('00970', 'MG_489'), ('00970', 'MG_490'), ('00970', 'MG_492'), ('00970', 'MG_493'), ('00970', 'MG_495'), ('00970', 'MG_496'), ('00970', 'MG_497'), ('00970', 'MG_499'), ('00970', 'MG_500'), ('00970', 'MG_501'), ('00970', 'MG_502'), ('00970', 'MG_503'), ('00970', 'MG_504'), ('00970', 'MG_506'), ('00970', 'MG_507'), ('00970', 'MG_508'), ('00970', 'MG_509'), ('00970', 'MG_510'), ('00970', 'MG_511'), ('00970', 'MG_512'), ('00970', 'MG_513'), ('00970', 'MG_514'), ('00970', 'MG_518'), ('00970', 'MG_519'), ('00970', 'MG_520'), ('00970', 'MG_523'), ('01100', 'MG_001'), ('01100', 'MG_006'), ('01100', 'MG_007'), ('01100', 'MG_013'), ('01100', 'MG_022'), ('01100', 'MG_023'), ('01100', 'MG_030'), ('01100', 'MG_031'), ('01100', 'MG_034'), ('01100', 'MG_037'), ('01100', 'MG_038'), ('01100', 'MG_047'), ('01100', 'MG_049'), ('01100', 'MG_051'), ('01100', 'MG_052'), ('01100', 'MG_053'), ('01100', 'MG_058'), ('01100', 'MG_062'), ('01100', 'MG_066'), ('01100', 'MG_099'), ('01100', 'MG_100'), ('01100', 'MG_107'), ('01100', 'MG_110'), ('01100', 'MG_111'), ('01100', 'MG_112'), ('01100', 'MG_114'), ('01100', 'MG_118'), ('01100', 'MG_128'), ('01100', 'MG_145'), ('01100', 'MG_171'), ('01100', 'MG_177'), ('01100', 'MG_190'), ('01100', 'MG_212'), ('01100', 'MG_215'), ('01100', 'MG_216'), ('01100', 'MG_227'), ('01100', 'MG_228'), ('01100', 'MG_229'), ('01100', 'MG_231'), ('01100', 'MG_240'), ('01100', 'MG_245'), ('01100', 'MG_247'), ('01100', 'MG_261'), ('01100', 'MG_262'), ('01100', 'MG_264'), ('01100', 'MG_270'), ('01100', 'MG_271'), ('01100', 'MG_272'), ('01100', 'MG_273'), ('01100', 'MG_274'), ('01100', 'MG_276'), ('01100', 'MG_299'), ('01100', 'MG_300'), ('01100', 'MG_301'), ('01100', 'MG_315'), ('01100', 'MG_330'), ('01100', 'MG_336'), ('01100', 'MG_340'), ('01100', 'MG_341'), ('01100', 'MG_357'), ('01100', 'MG_368'), ('01100', 'MG_371'), ('01100', 'MG_372'), ('01100', 'MG_382'), ('01100', 'MG_383'), ('01100', 'MG_391'), ('01100', 'MG_394'), ('01100', 'MG_396'), ('01100', 'MG_398'), ('01100', 'MG_399'), ('01100', 'MG_400'), ('01100', 'MG_401'), ('01100', 'MG_402'), ('01100', 'MG_403'), ('01100', 'MG_404'), ('01100', 'MG_405'), ('01100', 'MG_407'), ('01100', 'MG_419'), ('01100', 'MG_430'), ('01100', 'MG_431'), ('01100', 'MG_434'), ('01100', 'MG_437'), ('01100', 'MG_453'), ('01100', 'MG_458'), ('01100', 'MG_460'), ('01100', 'MG_462'), ('01100', 'MG_517'), ('01110', 'MG_023'), ('01110', 'MG_039'), ('01110', 'MG_047'), ('01110', 'MG_049'), ('01110', 'MG_053'), ('01110', 'MG_058'), ('01110', 'MG_066'), ('01110', 'MG_111'), ('01110', 'MG_112'), ('01110', 'MG_145'), ('01110', 'MG_171'), ('01110', 'MG_212'), ('01110', 'MG_215'), ('01110', 'MG_216'), ('01110', 'MG_247'), ('01110', 'MG_271'), ('01110', 'MG_272'), ('01110', 'MG_273'), ('01110', 'MG_274'), ('01110', 'MG_300'), ('01110', 'MG_301'), ('01110', 'MG_368'), ('01110', 'MG_394'), ('01110', 'MG_396'), ('01110', 'MG_407'), ('01110', 'MG_430'), ('01110', 'MG_431'), ('01110', 'MG_437'), ('01110', 'MG_458'), ('01110', 'MG_460'), ('01110', 'MG_462'), ('01120', 'MG_013'), ('01120', 'MG_023'), ('01120', 'MG_058'), ('01120', 'MG_062'), ('01120', 'MG_066'), ('01120', 'MG_111'), ('01120', 'MG_112'), ('01120', 'MG_190'), ('01120', 'MG_215'), ('01120', 'MG_216'), ('01120', 'MG_271'), ('01120', 'MG_272'), ('01120', 'MG_273'), ('01120', 'MG_274'), ('01120', 'MG_299'), ('01120', 'MG_300'), ('01120', 'MG_301'), ('01120', 'MG_357'), ('01120', 'MG_371'), ('01120', 'MG_394'), ('01120', 'MG_396'), ('01120', 'MG_407'), ('01120', 'MG_430'), ('01120', 'MG_431'), ('01120', 'MG_460'), ('01120', 'MG_462'), ('01130', 'MG_023'), ('01130', 'MG_053'), ('01130', 'MG_058'), ('01130', 'MG_066'), ('01130', 'MG_111'), ('01130', 'MG_112'), ('01130', 'MG_171'), ('01130', 'MG_215'), ('01130', 'MG_216'), ('01130', 'MG_271'), ('01130', 'MG_272'), ('01130', 'MG_273'), ('01130', 'MG_274'), ('01130', 'MG_300'), ('01130', 'MG_301'), ('01130', 'MG_394'), ('01130', 'MG_396'), ('01130', 'MG_407'), ('01130', 'MG_430'), ('01130', 'MG_431'), ('01130', 'MG_453'), ('01130', 'MG_460'), ('01200', 'MG_013'), ('01200', 'MG_023'), ('01200', 'MG_058'), ('01200', 'MG_066'), ('01200', 'MG_111'), ('01200', 'MG_112'), ('01200', 'MG_215'), ('01200', 'MG_216'), ('01200', 'MG_271'), ('01200', 'MG_272'), ('01200', 'MG_273'), ('01200', 'MG_274'), ('01200', 'MG_299'), ('01200', 'MG_300'), ('01200', 'MG_301'), ('01200', 'MG_357'), ('01200', 'MG_394'), ('01200', 'MG_396'), ('01200', 'MG_407'), ('01200', 'MG_430'), ('01200', 'MG_431'), ('01230', 'MG_023'), ('01230', 'MG_047'), ('01230', 'MG_058'), ('01230', 'MG_066'), ('01230', 'MG_112'), ('01230', 'MG_215'), ('01230', 'MG_216'), ('01230', 'MG_300'), ('01230', 'MG_301'), ('01230', 'MG_394'), ('01230', 'MG_396'), ('01230', 'MG_407'), ('01230', 'MG_430'), ('01230', 'MG_431'), ('02010', 'MG_042'), ('02010', 'MG_043'), ('02010', 'MG_044'), ('02010', 'MG_045'), ('02010', 'MG_077'), ('02010', 'MG_078'), ('02010', 'MG_079'), ('02010', 'MG_080'), ('02010', 'MG_179'), ('02010', 'MG_180'), ('02010', 'MG_181'), ('02010', 'MG_187'), ('02010', 'MG_289'), ('02010', 'MG_290'), ('02010', 'MG_291'), ('02010', 'MG_302'), ('02010', 'MG_303'), ('02010', 'MG_304'), ('02010', 'MG_410'), ('02010', 'MG_411'), ('02010', 'MG_412'), ('02020', 'MG_412'), ('02020', 'MG_469'), ('02024', 'MG_048'), ('02024', 'MG_055'), ('02024', 'MG_072'), ('02024', 'MG_077'), ('02024', 'MG_078'), ('02024', 'MG_079'), ('02024', 'MG_080'), ('02024', 'MG_170'), ('02024', 'MG_277'), ('02024', 'MG_297'), ('02024', 'MG_464'), ('02024', 'MG_476'), ('02060', 'MG_062'), ('02060', 'MG_069'), ('02060', 'MG_429'), ('03010', 'MG_070'), ('03010', 'MG_081'), ('03010', 'MG_082'), ('03010', 'MG_087'), ('03010', 'MG_088'), ('03010', 'MG_090'), ('03010', 'MG_092'), ('03010', 'MG_093'), ('03010', 'MG_150'), ('03010', 'MG_151'), ('03010', 'MG_152'), ('03010', 'MG_153'), ('03010', 'MG_154'), ('03010', 'MG_155'), ('03010', 'MG_156'), ('03010', 'MG_157'), ('03010', 'MG_158'), ('03010', 'MG_159'), ('03010', 'MG_160'), ('03010', 'MG_161'), ('03010', 'MG_162'), ('03010', 'MG_163'), ('03010', 'MG_164'), ('03010', 'MG_165'), ('03010', 'MG_166'), ('03010', 'MG_167'), ('03010', 'MG_168'), ('03010', 'MG_169'), ('03010', 'MG_174'), ('03010', 'MG_175'), ('03010', 'MG_176'), ('03010', 'MG_178'), ('03010', 'MG_197'), ('03010', 'MG_198'), ('03010', 'MG_232'), ('03010', 'MG_234'), ('03010', 'MG_257'), ('03010', 'MG_311'), ('03010', 'MG_325'), ('03010', 'MG_361'), ('03010', 'MG_362'), ('03010', 'MG_363'), ('03010', 'MG_417'), ('03010', 'MG_418'), ('03010', 'MG_424'), ('03010', 'MG_426'), ('03010', 'MG_444'), ('03010', 'MG_446'), ('03010', 'MG_466'), ('03010', 'MG_473'), ('03010', 'MG_481'), ('03010', 'MG_522'), ('03010', 'MG_rrnA16S'), ('03010', 'MG_rrnA23S'), ('03010', 'MG_rrnA5S'), ('03018', 'MG_104'), ('03018', 'MG_130'), ('03018', 'MG_139'), ('03018', 'MG_215'), ('03018', 'MG_305'), ('03018', 'MG_392'), ('03018', 'MG_407'), ('03018', 'MG_423'), ('03020', 'MG_022'), ('03020', 'MG_177'), ('03020', 'MG_340'), ('03020', 'MG_341'), ('03030', 'MG_001'), ('03030', 'MG_007'), ('03030', 'MG_010'), ('03030', 'MG_031'), ('03030', 'MG_091'), ('03030', 'MG_094'), ('03030', 'MG_250'), ('03030', 'MG_254'), ('03030', 'MG_261'), ('03030', 'MG_262'), ('03030', 'MG_315'), ('03030', 'MG_419'), ('03060', 'MG_0001'), ('03060', 'MG_048'), ('03060', 'MG_055'), ('03060', 'MG_072'), ('03060', 'MG_170'), ('03060', 'MG_210'), ('03060', 'MG_277'), ('03060', 'MG_297'), ('03060', 'MG_464'), ('03060', 'MG_476'), ('03070', 'MG_048'), ('03070', 'MG_055'), ('03070', 'MG_072'), ('03070', 'MG_170'), ('03070', 'MG_277'), ('03070', 'MG_297'), ('03070', 'MG_464'), ('03070', 'MG_476'), ('03410', 'MG_097'), ('03410', 'MG_235'), ('03410', 'MG_254'), ('03410', 'MG_262'), ('03410', 'MG_498'), ('03420', 'MG_073'), ('03420', 'MG_206'), ('03420', 'MG_244'), ('03420', 'MG_254'), ('03420', 'MG_262'), ('03420', 'MG_421'), ('03430', 'MG_001'), ('03430', 'MG_007'), ('03430', 'MG_031'), ('03430', 'MG_091'), ('03430', 'MG_244'), ('03430', 'MG_254'), ('03430', 'MG_261'), ('03430', 'MG_315'), ('03430', 'MG_419'), ('03440', 'MG_001'), ('03440', 'MG_007'), ('03440', 'MG_031'), ('03440', 'MG_091'), ('03440', 'MG_261'), ('03440', 'MG_262'), ('03440', 'MG_315'), ('03440', 'MG_339'), ('03440', 'MG_358'), ('03440', 'MG_359'), ('03440', 'MG_419'), ('04122', 'MG_295'), ('04122', 'MG_372')]
        kegg_ids, gene_codes = zip(*kegg_id_to_gene_code)

        return kegg_ids, gene_codes

# utilities
    def createLabelsForGenomes(self, np_array_of_genomes = None):
        """
        Takes a numpy array of genomes where rows are genomes and columns are genes and creates a label for each genome made up of two parts separated by and underscore. The first part is number of genes knockedout in the genome and the second part is the number of times that a genome with that amount of knockouts has occured. So if the current genome is the third genome found with sixty-five genes knocked out then we create the label '65_3'.
        """
        if np_array_of_genomes == None:
            genomes = self.genomes
        elif type(np_array_of_genomes) is np.ndarray:
            genomes = np_array_of_genomes
        else:
            raise TypeError('np_array_of_genomes must either be equal to None or have type numpy.ndarray. Here type(np_array_of_genomes) = ', type(np_array_of_genomes))

        no_of_genomes, no_of_genes = genomes.shape
        list_of_ko_sizes = [sum(genomes[genome_idx, :] == 0) for genome_idx in range(no_of_genomes)]
        unique_ko_sizes = list(set(list_of_ko_sizes))
        ko_size_to_count_dict = {ko_size: 1 for ko_size in unique_ko_sizes}

        list_of_genome_names = [0 for idx in range(no_of_genomes)]
        for genome_idx in range(no_of_genomes):
            list_of_genome_names[genome_idx] = str(list_of_ko_sizes[genome_idx]) + '_' + str(ko_size_to_count_dict[list_of_ko_sizes[genome_idx]])
            ko_size_to_count_dict[list_of_ko_sizes[genome_idx]] += 1

        if list_of_genome_names.count(0) != 0:
            raise ValueError('list_of_genome_names should not contain zeros - something must have gone wrong! list_of_genome_names.count(0) = ', list_of_genome_names.count(0))

        return list_of_genome_names

    def getJrClassification(self):
        jr_classifications_dict = {'non-essential': ('MG_009', 'MG_012', 'MG_014', 'MG_015', 'MG_020', 'MG_027', 'MG_029', 'MG_030', 'MG_033', 'MG_040', 'MG_046', 'MG_048', 'MG_050', 'MG_052', 'MG_055', 'MG_059', 'MG_061', 'MG_062', 'MG_063', 'MG_064', 'MG_065', 'MG_072', 'MG_075', 'MG_083', 'MG_085', 'MG_086', 'MG_097', 'MG_101', 'MG_476', 'MG_105', 'MG_109', 'MG_110', 'MG_119', 'MG_120', 'MG_121', 'MG_123', 'MG_127', 'MG_130', 'MG_132', 'MG_139', 'MG_143', 'MG_149', 'MG_170', 'MG_172', 'MG_183', 'MG_184', 'MG_187', 'MG_188', 'MG_189', 'MG_190', 'MG_191', 'MG_192', 'MG_200', 'MG_205', 'MG_208', 'MG_209', 'MG_210', 'MG_482', 'MG_213', 'MG_214', 'MG_217', 'MG_218', 'MG_225', 'MG_226', 'MG_227', 'MG_235', 'MG_236', 'MG_239', 'MG_240', 'MG_244', 'MG_252', 'MG_259', 'MG_262', 'MG_498', 'MG_264', 'MG_265', 'MG_277', 'MG_288', 'MG_289', 'MG_290', 'MG_291', 'MG_293', 'MG_298', 'MG_305', 'MG_309', 'MG_310', 'MG_312', 'MG_316', 'MG_317', 'MG_318', 'MG_324', 'MG_327', 'MG_329', 'MG_333', 'MG_336', 'MG_339', 'MG_344', 'MG_346', 'MG_352', 'MG_355', 'MG_356', 'MG_358', 'MG_359', 'MG_370', 'MG_376', 'MG_380', 'MG_385', 'MG_386', 'MG_390', 'MG_392', 'MG_393', 'MG_398', 'MG_399', 'MG_401', 'MG_403', 'MG_404', 'MG_405', 'MG_408', 'MG_409', 'MG_410', 'MG_411', 'MG_425', 'MG_427', 'MG_428', 'MG_438', 'MG_442', 'MG_447', 'MG_448', 'MG_454', 'MG_457', 'MG_460', 'MG_463', 'MG_464', 'MG_467', 'MG_468', 'MG_526'), 'Non-essential?': ('MG_039', 'MG_073', 'MG_104', 'MG_122', 'MG_186', 'MG_206', 'MG_297', 'MG_335', 'MG_349', 'MG_353', 'MG_369', 'MG_391', 'MG_402', 'MG_412', 'MG_421'), 'Blank': ('MG_141', 'MG_177', 'MG_238', 'MG_254', 'MG_341', 'MG_384', 'MG_400', 'MG_469', 'MG_470'), 'Septum': ('MG_003', 'MG_004', 'MG_019', 'MG_201', 'MG_203', 'MG_204', 'MG_221', 'MG_224', 'MG_387'), 'RNA': ('MG_249', 'MG_282', 'MG_340'), 'Protein': ('MG_005', 'MG_008', 'MG_021', 'MG_026', 'MG_035', 'MG_036', 'MG_049', 'MG_051', 'MG_473', 'MG_070', 'MG_081', 'MG_082', 'MG_084', 'MG_087', 'MG_088', 'MG_089', 'MG_090', 'MG_092', 'MG_093', 'MG_098', 'MG_099', 'MG_100', 'MG_106', 'MG_113', 'MG_126', 'MG_136', 'MG_142', 'MG_150', 'MG_151', 'MG_152', 'MG_153', 'MG_154', 'MG_155', 'MG_156', 'MG_157', 'MG_158', 'MG_159', 'MG_160', 'MG_161', 'MG_162', 'MG_163', 'MG_164', 'MG_165', 'MG_166', 'MG_167', 'MG_168', 'MG_169', 'MG_173', 'MG_174', 'MG_175', 'MG_176', 'MG_178', 'MG_182', 'MG_194', 'MG_195', 'MG_196', 'MG_197', 'MG_198', 'MG_481', 'MG_232', 'MG_234', 'MG_251', 'MG_253', 'MG_257', 'MG_258', 'MG_266', 'MG_283', 'MG_292', 'MG_295', 'MG_311', 'MG_325', 'MG_334', 'MG_345', 'MG_347', 'MG_361', 'MG_362', 'MG_363', 'MG_522', 'MG_365', 'MG_367', 'MG_372', 'MG_375', 'MG_378', 'MG_379', 'MG_417', 'MG_418', 'MG_424', 'MG_426', 'MG_433', 'MG_435', 'MG_444', 'MG_445', 'MG_446', 'MG_451', 'MG_455', 'MG_462', 'MG_465', 'MG_466'), 'Metabolic': ('MG_006', 'MG_013', 'MG_022', 'MG_023', 'MG_034', 'MG_037', 'MG_038', 'MG_041', 'MG_042', 'MG_043', 'MG_044', 'MG_045', 'MG_047', 'MG_053', 'MG_058', 'MG_066', 'MG_069', 'MG_071', 'MG_077', 'MG_078', 'MG_079', 'MG_080', 'MG_102', 'MG_107', 'MG_111', 'MG_112', 'MG_114', 'MG_118', 'MG_124', 'MG_128', 'MG_137', 'MG_145', 'MG_171', 'MG_179', 'MG_180', 'MG_181', 'MG_212', 'MG_215', 'MG_216', 'MG_228', 'MG_229', 'MG_230', 'MG_231', 'MG_245', 'MG_270', 'MG_271', 'MG_272', 'MG_273', 'MG_274', 'MG_275', 'MG_276', 'MG_278', 'MG_287', 'MG_299', 'MG_300', 'MG_301', 'MG_302', 'MG_303', 'MG_304', 'MG_321', 'MG_322', 'MG_323', 'MG_330', 'MG_517', 'MG_342', 'MG_351', 'MG_357', 'MG_368', 'MG_382', 'MG_383', 'MG_394', 'MG_396', 'MG_407', 'MG_429', 'MG_430', 'MG_431', 'MG_434', 'MG_437', 'MG_453', 'MG_458'), 'DNA': ('MG_001', 'MG_007', 'MG_031', 'MG_091', 'MG_094', 'MG_250', 'MG_261', 'MG_315', 'MG_419')}

        return jr_classifications_dict

    def getJrConditionalEssential(self):
        conditional_essential_genes = ('MG_289', 'MG_290', 'MG_291', 'MG_298', 'MG_305', 'MG_310', 'MG_427')

        return conditional_essential_genes
 
    # functions related to staticDB codes etc
    def getGeneInfoDict(self, tuple_of_gene_codes):
        dict_of_gene_info = self.db_conn.getGeneInfo(tuple_of_gene_codes)

        return dict_of_gene_info
        
    def getAllProteinGroups(self, gene_info_df, gene_code):
        list_of_protein_groups = eval('[\'' + "', '".join(gene_info_df['functional_unit'].loc[gene_code].split(", ")) + '\']')
        return list_of_protein_groups

    def getGeneInfoDf(self, tuple_of_gene_codes):
        dict_out = self.getGeneInfoDict(tuple_of_gene_codes)
        gene_info = pd.DataFrame(dict_out)
        gene_info = gene_info.set_index('code')

        return gene_info
                
    def getNotJr358Genes(self):
        all_genes_raw = self.db_conn.sendSqlToStaticDb('select code from genes')
        # output comes as a list of return code and stdout as a string (list of tuples). Check return is zero and format the string so it is an actual python object and then turn that into a easily usable list.
        if all_genes_raw[0] == 0:
            sql_out = eval(all_genes_raw[1].strip())
            all_codes = set([code[0] for code in sql_out])

        else:
            raise ValueError('Data retrieval from static.db failed with exit code: ', all_genes_raw[0])

        # get JR358
        jr358 = set(self.ko_code_to_id_dict.keys())
        removed_genes = all_codes.difference(jr358)
        return list(removed_genes)


    def getJr358Genes(self):
        """The function returns the 358 genes that Joshua Rees classified for potential KOs."""
        return ('MG_001', 'MG_003', 'MG_004', 'MG_005', 'MG_006', 'MG_007', 'MG_008', 'MG_009', 'MG_012', 'MG_013', 'MG_014', 'MG_015', 'MG_019', 'MG_020', 'MG_021', 'MG_022', 'MG_023', 'MG_026', 'MG_027', 'MG_029', 'MG_030', 'MG_031', 'MG_033', 'MG_034', 'MG_035', 'MG_036', 'MG_037', 'MG_038', 'MG_039', 'MG_040', 'MG_041', 'MG_042', 'MG_043', 'MG_044', 'MG_045', 'MG_046', 'MG_047', 'MG_048', 'MG_049', 'MG_050', 'MG_051', 'MG_052', 'MG_053', 'MG_055', 'MG_473', 'MG_058', 'MG_059', 'MG_061', 'MG_062', 'MG_063', 'MG_064', 'MG_065', 'MG_066', 'MG_069', 'MG_070', 'MG_071', 'MG_072', 'MG_073', 'MG_075', 'MG_077', 'MG_078', 'MG_079', 'MG_080', 'MG_081', 'MG_082', 'MG_083', 'MG_084', 'MG_085', 'MG_086', 'MG_087', 'MG_088', 'MG_089', 'MG_090', 'MG_091', 'MG_092', 'MG_093', 'MG_094', 'MG_097', 'MG_098', 'MG_099', 'MG_100', 'MG_101', 'MG_102', 'MG_476', 'MG_104', 'MG_105', 'MG_106', 'MG_107', 'MG_109', 'MG_110', 'MG_111', 'MG_112', 'MG_113', 'MG_114', 'MG_118', 'MG_119', 'MG_120', 'MG_121', 'MG_122', 'MG_123', 'MG_124', 'MG_126', 'MG_127', 'MG_128', 'MG_130', 'MG_132', 'MG_136', 'MG_137', 'MG_139', 'MG_141', 'MG_142', 'MG_143', 'MG_145', 'MG_149', 'MG_150', 'MG_151', 'MG_152', 'MG_153', 'MG_154', 'MG_155', 'MG_156', 'MG_157', 'MG_158', 'MG_159', 'MG_160', 'MG_161', 'MG_162', 'MG_163', 'MG_164', 'MG_165', 'MG_166', 'MG_167', 'MG_168', 'MG_169', 'MG_170', 'MG_171', 'MG_172', 'MG_173', 'MG_174', 'MG_175', 'MG_176', 'MG_177', 'MG_178', 'MG_179', 'MG_180', 'MG_181', 'MG_182', 'MG_183', 'MG_184', 'MG_186', 'MG_187', 'MG_188', 'MG_189', 'MG_190', 'MG_191', 'MG_192', 'MG_194', 'MG_195', 'MG_196', 'MG_197', 'MG_198', 'MG_200', 'MG_201', 'MG_203', 'MG_204', 'MG_205', 'MG_206', 'MG_208', 'MG_209', 'MG_210', 'MG_481', 'MG_482', 'MG_212', 'MG_213', 'MG_214', 'MG_215', 'MG_216', 'MG_217', 'MG_218', 'MG_221', 'MG_224', 'MG_225', 'MG_226', 'MG_227', 'MG_228', 'MG_229', 'MG_230', 'MG_231', 'MG_232', 'MG_234', 'MG_235', 'MG_236', 'MG_238', 'MG_239', 'MG_240', 'MG_244', 'MG_245', 'MG_249', 'MG_250', 'MG_251', 'MG_252', 'MG_253', 'MG_254', 'MG_257', 'MG_258', 'MG_259', 'MG_261', 'MG_262', 'MG_498', 'MG_264', 'MG_265', 'MG_266', 'MG_270', 'MG_271', 'MG_272', 'MG_273', 'MG_274', 'MG_275', 'MG_276', 'MG_277', 'MG_278', 'MG_282', 'MG_283', 'MG_287', 'MG_288', 'MG_289', 'MG_290', 'MG_291', 'MG_292', 'MG_293', 'MG_295', 'MG_297', 'MG_298', 'MG_299', 'MG_300', 'MG_301', 'MG_302', 'MG_303', 'MG_304', 'MG_305', 'MG_309', 'MG_310', 'MG_311', 'MG_312', 'MG_315', 'MG_316', 'MG_317', 'MG_318', 'MG_321', 'MG_322', 'MG_323', 'MG_324', 'MG_325', 'MG_327', 'MG_329', 'MG_330', 'MG_333', 'MG_334', 'MG_335', 'MG_517', 'MG_336', 'MG_339', 'MG_340', 'MG_341', 'MG_342', 'MG_344', 'MG_345', 'MG_346', 'MG_347', 'MG_349', 'MG_351', 'MG_352', 'MG_353', 'MG_355', 'MG_356', 'MG_357', 'MG_358', 'MG_359', 'MG_361', 'MG_362', 'MG_363', 'MG_522', 'MG_365', 'MG_367', 'MG_368', 'MG_369', 'MG_370', 'MG_372', 'MG_375', 'MG_376', 'MG_378', 'MG_379', 'MG_380', 'MG_382', 'MG_383', 'MG_384', 'MG_385', 'MG_386', 'MG_387', 'MG_390', 'MG_391', 'MG_392', 'MG_393', 'MG_394', 'MG_396', 'MG_398', 'MG_399', 'MG_400', 'MG_401', 'MG_402', 'MG_403', 'MG_404', 'MG_405', 'MG_407', 'MG_408', 'MG_409', 'MG_410', 'MG_411', 'MG_412', 'MG_417', 'MG_418', 'MG_419', 'MG_421', 'MG_424', 'MG_425', 'MG_426', 'MG_427', 'MG_428', 'MG_429', 'MG_430', 'MG_431', 'MG_433', 'MG_434', 'MG_435', 'MG_437', 'MG_438', 'MG_442', 'MG_444', 'MG_445', 'MG_446', 'MG_447', 'MG_448', 'MG_451', 'MG_453', 'MG_454', 'MG_455', 'MG_457', 'MG_458', 'MG_460', 'MG_462', 'MG_463', 'MG_464', 'MG_465', 'MG_466', 'MG_467', 'MG_468', 'MG_526', 'MG_470')

    def getDictOfJr358Codes(self):
        """Creates a dictionary who's keys are Joshua Rees 358 gene codes and values are the gene ID acording to our database."""
        # get joshua rees' 358 gene codes
        jr358_codes = self.getJr358Genes()
        # use staticDB to create the dictionary
        code2id_dict = self.db_conn.convertGeneCodeToId(jr358_codes)

        return code2id_dict

    def invertDictionary(self, input_dict):
        """This function takes a dictionary and inverts it (assuming it's one to one)."""
        inverse_dict = {v: k for k, v in input_dict.items()}

        return inverse_dict

    def createIdxToIdDict(self, code_to_id_dict):
        list_of_ids = list(code_to_id_dict.values())
        # sort them into ascending order (just because the order of dicts aren't alwayys preserved and so provided we are using the same JR genes to start with we can compare the indexs provided they are ordered in ascending order) maybe not neccessary but avoiding hard to find bug later on
        list_of_ids.sort()
        idx_to_id_dict = {idx: list_of_ids[idx] for idx in range(len(list_of_ids))}

        return idx_to_id_dict

    def createIdToCodeDict(self):
        id_to_code_dict = self.invertDictionary(self.ko_code_to_id_dict)

        return id_to_code_dict

    def convertIdxToGeneId(self, gene_indexs_list, index_to_id_dict):
        """
        """
        # test input is of the right form
        if not (type(gene_indexs_list) is list and type(index_to_id_dict) is dict):
            raise TypeError('gene_indexs_list must be a list (even if only one value!) and index_to_id_dict must be a dictionary. Here type(gene_indexs_list)=', type(gene_indexs_list), ' and type(index_to_id_dict)=', type(index_to_id_dict))

        gene_id_list = [index_to_id_dict[idx] for idx in gene_indexs_list]

        return gene_id_list

    def convertGeneIdToCode(self, gene_id_list):
        """
        """
        # test input is of the right form
        if not (type(gene_id_list) is list):
            raise TypeError('gene_id_list must be a list (even if only one value!). Here type(gene_indexs_list)=', type(gene_indexs_list))

        gene_id_list = [self.ko_id_to_code_dict[ID] for ID in gene_id_list]

        return gene_id_list

if __name__ == "__main__":
    mgs_inst = MGS()
    ko_sets = mgs_inst.getHistoricalMGSs()
    mgs_genomes, ko_set_names_in_order = mgs_inst.convertKoListsToGenomes()
    mgs_inst.plotGenomes(mgs_genomes)
    distance_matrix = mgs_inst.createAriDistanceMatrix()
    genomes_dbscan = mgs_inst.orderGeneomesWithDbscan(distance_matrix)
    mgs_inst.plotGenomes(genomes_dbscan)
    mgs_inst.plotDendogramOfMGSs(distance_matrix)
    print(mgs_inst.sumeriseEssentialityByGene())

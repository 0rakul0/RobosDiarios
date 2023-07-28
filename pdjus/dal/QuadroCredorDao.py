from pdjus.dal.GenericoDao import GenericoDao,Singleton
from pdjus.modelo.BlocoQuadro import BlocoQuadro
from pdjus.dal.GenericoDao import GenericoDao,Singleton, fn
from pdjus.modelo.QuadroCredor import QuadroCredor
from pdjus.modelo.BlocoQuadro import BlocoQuadro
from pdjus.modelo.Processo import Processo
from pdjus.modelo.ClasseCredor import ClasseCredor
from util.StringUtil import remove_acentos,remove_varios_espacos,remove_caracteres_especiais

class QuadroCredorDao(GenericoDao,metaclass=Singleton):
    def __init__(self):
        super(QuadroCredorDao, self).__init__(QuadroCredor)

    def get_por_processo_nome_data_moeda_valor_classe_credor_fonte(self,processo,nome,data,tipo_moeda,valor,classe_credor,fonte_dado):
        try:
            nome = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(nome.upper())))

            return self._classe.select().where((self._classe.processo == processo),(self._classe.classe_credor == classe_credor), (self._classe._nome == nome) ,
                (self._classe.data == data),(self._classe.tipo_moeda == tipo_moeda),(self._classe.valor == valor),(self._classe.fonte_dado == fonte_dado)).get()
        except self._classe.DoesNotExist as e:
            return None
    def get_por_processo_nome_data_moeda_valor_classe_credor_fonte_bloco(self,processo,nome,data,tipo_moeda,valor,classe_credor,fonte_dado,bloco_quadro):
        try:
            nome = remove_varios_espacos(remove_acentos(remove_caracteres_especiais(nome.upper())))

            return self._classe.select().where((self._classe.processo == processo),(self._classe.classe_credor == classe_credor), (self._classe._nome == nome) ,
                (self._classe.data == data),(self._classe.tipo_moeda == tipo_moeda),(self._classe.valor == valor),(self._classe.fonte_dado == fonte_dado),
                                               (self._classe.bloco_quadro == bloco_quadro)).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_credores_por_data(self, processo, data):
        try:
            return self._classe.select().join(Processo).\
                where(Processo.id == processo.id, self._classe.data == data ).get()
        except self._classe.DoesNotExist as e:
            return None

    def get_credores_por_data_e_classe_credor(self, processo, data, classe_credor):
        try:
            return self._classe.select().join(Processo).join(self._classe.classe_credor).\
                where(Processo.id == processo.id, self._classe.data == data, ClasseCredor.id == classe_credor.id)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_processo_id(self, processo_id):
        try:
            return self._classe.select().join(Processo). \
                where(Processo.id == processo_id)
        except self._classe.DoesNotExist as e:
            return None

    def get_por_bloco_quadro_id(self, bloco_quadro_id):
        try:
            return self._classe.select().join(BlocoQuadro). \
                where(BlocoQuadro.id == bloco_quadro_id)
        except self._classe.DoesNotExist as e:
            return None
    def get_credores_que_precisam_ser_corrigidos(self,nome):
        try:
            return self._classe.select().join(BlocoQuadro).where((BlocoQuadro.id << [8, 75, 93, 101, 121, 125, 141, 192, 292, 357, 370, 392, 393, 395, 402, 464, 546, 550, 565, 589, 592, 596, 600, 691, 694, 695, 704, 706, 738, 768, 769, 846, 852, 872, 938, 948, 964, 987, 993, 999, 1019, 1027, 1061, 1074, 1080, 1087, 1090, 1101, 1103, 1105, 1113, 1122, 1128, 1129, 1157, 1164, 1165, 1181, 1185, 1194, 1195, 1210, 1229, 1231, 1249, 1253, 1264, 1294, 1295, 1318, 1321, 1336, 1344, 1347, 1421, 1490, 1516, 1539, 1546, 1549, 1590, 1630, 1638, 1652, 1653, 1677, 1699, 1734, 1777, 1836, 1840, 1859, 1865, 1874, 1875, 1885, 1895, 1974, 2038, 2086, 2092, 2117, 2120, 2127, 2141, 2142, 2153, 2156, 2172, 2176, 2209, 2215, 2217, 2221, 2222, 2223, 2225, 2233, 2236, 2239, 2241, 2250, 2279, 2293, 2294, 2301, 2302, 2317, 2326, 2339, 2363, 2378, 2384, 2390, 2398, 2409, 2413, 2442, 2445, 2446, 2452, 2459, 2468, 2471, 2487, 2499, 2501, 2510, 2516, 2518, 2530, 2537, 2538, 2551, 2604, 2645, 2649, 2724, 2735, 2741, 2758, 2761, 2764, 2772, 2775, 2780, 2788, 2794, 2807, 2815, 2822, 2832, 2866, 2871, 2873, 2877, 2878, 2879, 2881, 2887, 2898, 2909, 2912, 2922, 2923, 2935, 2938, 2947, 2970, 2973, 2982, 2987, 2994, 3000, 3001, 3002, 3010, 3013, 3016, 3023, 3024, 3042, 3061, 3074, 3082, 3094, 3097, 3098, 3102, 3137, 3161, 3180, 3184, 3191, 3206, 3253, 3255, 3272, 3278, 3296, 3302, 3305, 3312, 3323, 3328, 3329, 3335, 3367, 3375, 3385, 3387, 3405, 3410, 3428, 3438, 3451, 3452, 3455, 3477, 3482, 3485, 3494, 3502, 3509, 3520, 3537, 3542, 3545, 3598, 3670, 4038, 4050, 4165, 4225, 5140, 5526, 5537, 5551, 5665, 5856, 6145, 6362, 6577, 6745, 6909, 7096, 7116, 7656, 7704, 8599, 9450, 9745, 9752, 9906, 10207, 10461, 10541, 10554, 11208, 11432, 11499, 11581, 11606, 11608, 11686, 11814, 11865, 11994, 12022, 12362, 12415, 12512, 12682, 12798, 12835, 12836, 13540, 13815, 14207, 14470, 14597, 14898, 15047, 15187, 15564, 15981, 15996, 16005, 16014, 16638, 16641, 16669, 16671, 16674, 16691, 16697, 16713, 16716, 16717, 16718, 16721, 16726, 16734, 16742, 16743, 16746, 16751, 16757, 16770, 16774, 16777, 16780, 16784, 16787, 16788, 16789, 16795, 16803, 16806, 16819, 16822, 16843, 16852, 16858, 16861, 16891, 16896, 16897, 16899, 16911, 16968, 16973, 16974, 16977, 16980, 16981, 16982, 16985, 16988, 16994, 17002, 17003, 17007, 17011, 17013, 17015, 17020, 17023, 17025, 17033, 17039, 17044, 17046, 17047, 17052, 17057, 17066, 17067, 17068, 17069, 17072, 17074, 17079, 17107, 17109, 17114, 17134, 17149, 17161, 17184, 17190, 17191, 17197, 17200, 17203, 17208, 17216, 17221, 17227, 17232, 17235, 17240, 17244, 17246, 17247, 17249, 17255, 17269, 17283, 17284, 17289, 17295, 17299, 17301, 17302, 17306, 17309, 17322, 17325, 17330, 17334, 17339, 17340, 17349, 17353, 17378, 17397, 17399, 17406, 17414, 17419, 17438, 17458, 17466, 17471, 17474, 17484, 17511, 17514, 17518, 17536, 17542, 17546, 17548, 17553, 17555, 17556, 17559, 17564, 17569, 17576, 17577, 17578, 17581, 17585, 17590, 17594, 17596, 17604, 17609, 17618, 17628, 17632, 17643, 17650, 17652, 17655, 17656, 17657, 17660, 17662, 17668, 17677, 17701, 17709, 17736, 17741, 17744, 17754, 17755, 17759, 17762, 17785, 17786, 17790, 17819, 17820, 17823, 17825, 17838, 17849, 17850, 17859, 17866, 17868, 17880, 17881, 17886, 17895, 17902, 17904, 17907, 17913, 17917, 17922, 17928, 17931, 17939, 17940, 17953, 17955, 17969, 17970, 17971, 17977, 17980, 17985, 17989, 17990, 17994, 17998, 18001, 18005, 18008, 18017, 18018, 18020, 18024, 18026, 18029, 18035, 18045, 18047, 18048, 18049, 18054, 18060, 18061, 18062, 18072, 18078, 18083, 18084, 18085, 18089, 18097, 18100, 18102, 18104, 18114, 18115, 18120, 18124, 18127, 18132, 18154, 18155, 18161, 18165, 18168, 18171, 18174, 18175, 18181, 18184, 18194, 18198, 18202, 18210, 18211, 18213, 18222, 18227, 18236, 18240, 18241, 18250, 18253, 18261, 18268, 18271, 18272, 18273, 18277, 18279]) & (fn.Length(self._classe._nome) < 500) & self._classe._nome.regexp(nome))

        except self._classe.DoesNotExist as e:
            return None
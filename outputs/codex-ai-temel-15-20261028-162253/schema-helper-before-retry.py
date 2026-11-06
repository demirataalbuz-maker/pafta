"""Lesson 14: real JSON-schema decoding on a private CPU Ollama server.

Never unloads models from the user's or another agent's server. No downloads.
Official protocol: https://docs.ollama.com/capabilities/structured-outputs
"""
import copy
import json
import secrets
import time
from sandbox import ai_gercek_lab as lab

SCHEMA = {
    'type': 'object',
    'properties': {
        'islem': {'type': 'string', 'enum': ['not_ekle', 'raporla']},
        'deger': {'type': 'string', 'minLength': 1, 'maxLength': 80},
        'onay': {'type': 'boolean'},
    },
    'required': ['islem', 'deger', 'onay'],
    'additionalProperties': False,
}


class OzelCpuOturumu(lab.SohbetOturumu):
    def __init__(self):
        super().__init__()
        # Force the base context manager down its owned-server branch.
        # It chooses its own free loopback port before launching ollama serve.
        self.adres = f'http://127.0.0.1:{lab._bos_port()}'

    def semali_cagir(self, prompt, seed):
        if self.surec is None or self.surec.poll() is not None:
            raise lab.GercekLabYok('Deneye ait canlı Ollama süreci yok; başka sunucu kullanılmaz.')
        request = {'model': self.model, 'messages': [
            {'role': 'system', 'content': 'Return only the requested JSON object. No markdown or commentary.'},
            {'role': 'user', 'content': prompt + '\nJSON schema: ' + json.dumps(SCHEMA)}],
            'stream': False, 'format': copy.deepcopy(SCHEMA),
            'options': {'temperature': 0, 'seed': seed, 'num_predict': 96, 'num_ctx': 1024, 'num_gpu': 0},
            'keep_alive': '2m'}
        if self.dusunme:
            request['think'] = False
        start = time.perf_counter()
        response = lab._istek(self.adres, '/api/chat', request, sure=120)
        if response.get('done') is not True or response.get('done_reason') == 'length':
            raise lab.GercekLabYok('JSON Schema gerçek üretimi tamamlanmadı veya token sınırında kesildi.')
        return {'istek': request, 'ham_yanit': response,
                'icerik': (response.get('message') or {}).get('content', ''),
                'sure_ms': round((time.perf_counter()-start)*1000)}

    def __exit__(self, *exc):
        if self.surec is None:
            self.kayit['temizlik'] = {'not': 'Sahipli süreç yok; hiçbir model boşaltılmadı.'}
            return False
        return super().__exit__(*exc)


def gercek_ciktilar():
    records = []
    initial_user_server = lab._canli(lab._adres())
    with OzelCpuOturumu() as session:
        for i, operation in enumerate(['raporla', 'not_ekle']):
            marker = 'PAFTA-' + secrets.token_hex(4).upper()
            prompt = f'A synthetic note: islem={operation}, deger={marker}, onay=false. Copy these values into the object.'
            result = session.semali_cagir(prompt, secrets.randbelow(10**6))
            records.append(dict(result, beklenen={'islem': operation, 'deger': marker, 'onay': False}))
        environment = copy.deepcopy(session.kayit)
        environment['bellek'] = session.bellek()
    environment['temizlik'] = session.kayit.get('temizlik')
    environment['kullanici_sunucu_once'] = initial_user_server
    environment['kullanici_sunucu_sonra'] = lab._canli(lab._adres())
    return records, environment

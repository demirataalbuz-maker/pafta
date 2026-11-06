"""ai-temel-11: real frozen LM logits + trainable token-bias policy.

No fixtures, downloads or server calls. Only this lesson imports this helper.
The base LM is evaluated once per prompt; only an additive output bias trains.
"""
import hashlib
import random


def hazirla():
    import torch
    from sandbox import ai_gercek_lab as lab
    tok, model, bilgi = lab.dil_modeli()
    seed = random.SystemRandom().randrange(1, 2**31)
    rng = random.Random(seed)
    pairs = [(' yes', ' no'), (' left', ' right'), (' red', ' blue')]
    contexts = [f'Training sample {rng.randrange(10000,99999)}: choose a label.',
                f'An invented direction exercise {rng.randrange(10000,99999)}: choose a label.',
                f'An invented color exercise {rng.randrange(10000,99999)}: choose a label.']
    bases, cases, raw = {}, [], []
    for prompt, (chosen, rejected) in zip(contexts, pairs):
        ids = tok(prompt, add_special_tokens=False)['input_ids']
        c = tok(chosen, add_special_tokens=False)['input_ids'][0]
        r = tok(rejected, add_special_tokens=False)['input_ids'][0]
        if c == r:
            raise lab.GercekLabYok('Seçilen ve reddedilen gerçek token kimlikleri aynı.')
        with torch.no_grad():
            logits = model(torch.tensor([ids]), use_cache=False).logits[0, -1].double().detach().clone()
        bases[prompt] = logits
        cases.append({'prompt': prompt, 'chosen': c, 'rejected': r})
        raw.append({'prompt': prompt, 'token_idleri': ids, 'chosen': c, 'rejected': r,
                    'chosen_metin': tok.decode([c]), 'rejected_metin': tok.decode([r]),
                    'chosen_logit': logits[c].item(), 'rejected_logit': logits[r].item(),
                    'logit_sha256': hashlib.sha256(logits.numpy().tobytes()).hexdigest()})
    info = dict(bilgi, uyarlama='Yalnız sözlük boyutlu ek çıktı biası; LM ağırlıkları eğitilmez.',
                protokol='Gerçek son-konum logitleri; tek tokenlık chosen/rejected tamamlamalar.',
                veri_tohumu=seed, gercek_cagrilar=raw)
    return bases, cases, info


def modeller(bases, lr):
    import torch
    class Politika(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.token_bias = torch.nn.Parameter(torch.zeros_like(next(iter(bases.values()))))
        def forward(self, prompt):
            return bases[prompt] + self.token_bias
    class Referans(torch.nn.Module):
        def forward(self, prompt):
            return bases[prompt].clone()
    policy, reference = Politika(), Referans()
    return policy, reference, torch.optim.SGD(policy.parameters(), lr=lr, momentum=0, weight_decay=0)

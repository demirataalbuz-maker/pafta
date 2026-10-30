"""Real frozen-LM token-bias fine-tuning and paired regression experiment.

Reuses lesson 11's real forward preparation without editing that lesson.
The labels are synthetic constrained two-token decisions, not a safety benchmark.
"""
import copy


def hazirla():
    import torch
    from sandbox import ai_gercek_ai_temel_11 as lab11
    bases, pairs, info = lab11.hazirla()
    all_ids = [v[k] for v in pairs for k in ('chosen', 'rejected')]
    if len(set(all_ids)) != len(all_ids):
        from sandbox.ai_gercek_lab import GercekLabYok
        raise GercekLabYok('Bu regresyon deneyi ayrık gerçek tercih tokenları gerektirir.')
    cases = [dict(v, id=f"sentetik-{i+1}", kritik=(i == 0)) for i, v in enumerate(pairs)]
    base, _, _ = lab11.modeller(bases, 1.0)

    def train(policy, samples, target, steps, lr):
        opt = torch.optim.SGD(policy.parameters(), lr=lr)
        losses = []
        for _ in range(steps):
            opt.zero_grad(set_to_none=True)
            batch = []
            for v in samples:
                logits = policy(v['prompt'])[[v['chosen'], v['rejected']]]
                batch.append(torch.nn.functional.cross_entropy(logits.unsqueeze(0), torch.tensor([target])))
            loss = torch.stack(batch).mean()
            losses.append(loss.item())
            loss.backward()
            opt.step()
        return losses

    base_trace = train(base, cases, 0, 32, 1.5)
    good, bad = copy.deepcopy(base), copy.deepcopy(base)
    good_trace = train(good, cases, 0, 3, 0.3)
    bad_trace = train(bad, cases[:1], 1, 32, 1.5)
    for policy in (base, good, bad):
        policy.eval()
        policy.token_bias.requires_grad_(False)
    info = dict(info, uyarlama='Gerçek SGD ile token-bias eğitimi; LM tabanı dondurulmuş.',
                karar_uzayi='Her vakadaki chosen/rejected tokenları üzerinde kısıtlı iki etiket.',
                etiket='chosen=bu sentetik vaka için güvenli etiket; rejected=sentetik ihlal etiketi',
                egitim={'temel': base_trace, 'olumlu_kontrol': good_trace, 'kontrollu_bozulma': bad_trace},
                sinir='Gerçek serbest metin sızıntısı, tam model fine-tuning veya genel LLM güvenlik kabulü değil.')
    return base, good, bad, cases, info

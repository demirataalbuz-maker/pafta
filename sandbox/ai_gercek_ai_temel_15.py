"""Real residual-stream direction extraction for lesson 15. No downloads."""
import hashlib


def agirlik_ozeti(model):
    h = hashlib.sha256()
    for name, p in model.named_parameters():
        h.update(name.encode('utf-8') + b'\0')
        h.update(p.detach().contiguous().cpu().numpy().tobytes())
    return h.hexdigest()


def hazirla():
    import torch
    from sandbox import ai_gercek_lab as lab
    tok, model, info = lab.dil_modeli()
    layers = getattr(getattr(model, 'model', None), 'layers', None)
    if layers is None or len(layers) < 4:
        raise lab.GercekLabYok('Bu deney Llama-benzeri decoder katmanları gerektirir.')
    positive = ['The report is calm and clear.', 'A quiet and careful explanation.']
    negative = ['The report is urgent and loud.', 'A hurried and noisy explanation.']
    directions, records = {}, []
    for index in (0, 2):
        groups = []
        for texts in (positive, negative):
            states = []
            for text in texts:
                found = []
                def capture(module, args, output):
                    tensor = output[0] if isinstance(output, tuple) else output
                    found.append(tensor[0, -1].detach().double().clone())
                handle = layers[index].register_forward_hook(capture)
                try:
                    with torch.no_grad():
                        ids = tok(text, add_special_tokens=False)['input_ids']
                        model(torch.tensor([ids]), use_cache=False)
                finally:
                    handle.remove()
                states.append(found[0])
            groups.append(torch.stack(states).mean(0))
        direction = groups[0]-groups[1]
        norm = torch.linalg.vector_norm(direction)
        if not bool(torch.isfinite(norm)) or norm.item() == 0:
            raise lab.GercekLabYok('Gerçek aktivasyon farkından sıfır/sonlu olmayan yön çıktı.')
        direction = (direction/norm).detach()
        directions[index] = direction
        records.append({'katman': index, 'pozitif': positive, 'negatif': negative,
                        'fark_normu': norm.item(), 'yon_normu': torch.linalg.vector_norm(direction).item(),
                        'yon_sha256': hashlib.sha256(direction.numpy().tobytes()).hexdigest(),
                        'boyut': direction.numel()})
    return tok, model, directions, dict(info, yon_cikarma=records,
        sinir='Sentetik karşıt metinlerin aktivasyon farkı; semantik/refusal veya güvenlik yönü kabulü değil.')

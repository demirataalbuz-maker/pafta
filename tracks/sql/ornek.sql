-- Pafta SQL yolu · örnek veritabanı
-- Küçük bir şirketin BT operasyonu. Her çalıştırmada bellek içinde sıfırdan kurulur:
-- yaptığın INSERT/UPDATE/DELETE bir sonraki çalıştırmada kaybolur.

CREATE TABLE ekipler (
    id      INTEGER PRIMARY KEY,
    ad      TEXT NOT NULL UNIQUE,
    vardiya TEXT NOT NULL CHECK (vardiya IN ('gündüz', 'gece'))
);

INSERT INTO ekipler (id, ad, vardiya) VALUES
    (1, 'Altyapı',    'gündüz'),
    (2, 'Veritabanı', 'gündüz'),
    (3, 'Ağ',         'gece'),
    (4, 'Uygulama',   'gündüz'),
    (5, 'Arşiv',      'gece');

CREATE TABLE personel (
    id          INTEGER PRIMARY KEY,
    ad          TEXT NOT NULL,
    ekip_id     INTEGER REFERENCES ekipler(id),      -- NULL: henüz bir ekibe atanmadı
    unvan       TEXT NOT NULL,
    yonetici_id INTEGER REFERENCES personel(id),     -- NULL: en üst yönetici
    ise_giris   TEXT NOT NULL                        -- YYYY-AA-GG
);

INSERT INTO personel (id, ad, ekip_id, unvan, yonetici_id, ise_giris) VALUES
    (1,  'Selin',  1,    'BT Müdürü',             NULL, '2019-03-01'),
    (2,  'Kerem',  1,    'Sistem Yöneticisi',     1,    '2021-06-14'),
    (3,  'Ayşe',   2,    'Veritabanı Yöneticisi', 1,    '2020-01-20'),
    (4,  'Mert',   3,    'Ağ Uzmanı',             1,    '2022-09-05'),
    (5,  'Zeynep', 4,    'Yazılım Geliştirici',   1,    '2023-02-13'),
    (6,  'Can',    1,    'Sistem Yöneticisi',     2,    '2024-04-01'),
    (7,  'Elif',   3,    'Ağ Uzmanı',             4,    '2024-11-18'),
    (8,  'Burak',  NULL, 'Stajyer',               2,    '2026-07-01'),
    (9,  'Deniz',  4,    'Yazılım Geliştirici',   5,    '2025-05-12'),
    (10, 'Ece',    2,    'Veritabanı Yöneticisi', 3,    '2025-09-01');

CREATE TABLE sunucular (
    id         INTEGER PRIMARY KEY,
    ad         TEXT NOT NULL UNIQUE,
    rol        TEXT NOT NULL,
    isletim    TEXT NOT NULL,
    sehir      TEXT,                                 -- NULL: bulutta
    cpu        INTEGER NOT NULL,                     -- anlık CPU kullanımı (%)
    ram_gb     INTEGER,                              -- NULL: kayıtlı değil
    sorumlu_id INTEGER REFERENCES personel(id),      -- NULL: sorumlusu yok
    devreye    TEXT NOT NULL                         -- devreye alınma tarihi
);

INSERT INTO sunucular (id, ad, rol, isletim, sehir, cpu, ram_gb, sorumlu_id, devreye) VALUES
    (1,  'web01',    'web',        'Ubuntu 24.04',        'İstanbul', 72, 16,   2,    '2023-01-10'),
    (2,  'web02',    'web',        'Ubuntu 24.04',        'İstanbul', 65, 16,   2,    '2023-01-10'),
    (3,  'web03',    'web',        'Ubuntu 22.04',        'Ankara',   18, 8,    6,    '2021-05-03'),
    (4,  'db01',     'veritabanı', 'Debian 12',           'İstanbul', 91, 64,   3,    '2022-03-15'),
    (5,  'db02',     'veritabanı', 'Debian 12',           'Ankara',   47, 64,   10,   '2024-02-01'),
    (6,  'dc01',     'dizin',      'Windows Server 2022', 'İstanbul', 33, 32,   2,    '2022-08-20'),
    (7,  'dc02',     'dizin',      'Windows Server 2019', 'İzmir',    29, 16,   6,    '2020-11-11'),
    (8,  'cache01',  'önbellek',   'Ubuntu 24.04',        NULL,       84, 32,   5,    '2025-01-07'),
    (9,  'yedek01',  'yedek',      'Debian 12',           'İzmir',    12, NULL, 6,    '2019-06-30'),
    (10, 'izleme01', 'izleme',     'Ubuntu 22.04',        NULL,       55, 8,    4,    '2024-06-18'),
    (11, 'vpn01',    'ağ geçidi',  'Debian 12',           'Ankara',   38, 4,    7,    '2025-03-03'),
    (12, 'test01',   'test',       'Ubuntu 24.04',        NULL,       3,  4,    NULL, '2026-09-01');

CREATE TABLE biletler (
    id        INTEGER PRIMARY KEY,
    baslik    TEXT NOT NULL,
    sunucu_id INTEGER REFERENCES sunucular(id),      -- NULL: bir sunucuyla ilgili değil
    acan_id   INTEGER NOT NULL REFERENCES personel(id),
    atanan_id INTEGER REFERENCES personel(id),       -- NULL: henüz kimseye atanmadı
    oncelik   TEXT NOT NULL CHECK (oncelik IN ('düşük', 'orta', 'yüksek', 'kritik')),
    durum     TEXT NOT NULL CHECK (durum IN ('açık', 'çözüldü')),
    acilis    TEXT NOT NULL,                         -- 'YYYY-AA-GG SS:DD'
    kapanis   TEXT                                   -- NULL: hâlâ açık
);

INSERT INTO biletler (id, baslik, sunucu_id, acan_id, atanan_id, oncelik, durum, acilis, kapanis) VALUES
    (1,  'Disk doluluğu %90''ı aştı',          4,    3,  3,    'yüksek', 'çözüldü', '2026-10-12 08:15', '2026-10-12 11:45'),
    (2,  'TLS sertifikası 7 gün içinde bitiyor', 1,  2,  2,    'orta',   'çözüldü', '2026-10-12 09:00', '2026-10-13 10:00'),
    (3,  'Raporlama sorgusu yavaş',            4,    5,  3,    'orta',   'açık',    '2026-10-12 14:20', NULL),
    (4,  'Gece yedeklemesi tamamlanmadı',      9,    6,  6,    'kritik', 'çözüldü', '2026-10-13 07:05', '2026-10-13 09:35'),
    (5,  'Güvenlik yaması uygulanacak',        6,    1,  2,    'yüksek', 'açık',    '2026-10-13 10:30', NULL),
    (6,  'Önbellek isabet oranı düştü',        8,    9,  5,    'düşük',  'çözüldü', '2026-10-13 16:00', '2026-10-15 12:00'),
    (7,  'VPN bağlantısı kopuyor',             11,   4,  7,    'yüksek', 'çözüldü', '2026-10-14 08:40', '2026-10-14 13:10'),
    (8,  'Web sunucusu 502 dönüyor',           1,    5,  2,    'kritik', 'çözüldü', '2026-10-14 11:00', '2026-10-14 11:50'),
    (9,  'Replikasyon gecikmesi',              5,    10, NULL, 'yüksek', 'açık',    '2026-10-14 15:30', NULL),
    (10, 'Log dönüşümü ayarlanacak',           10,   4,  4,    'düşük',  'açık',    '2026-10-15 09:10', NULL),
    (11, 'DNS kaydı eklenecek',                6,    9,  6,    'düşük',  'çözüldü', '2026-10-15 10:00', '2026-10-15 10:30'),
    (12, 'RAM artırımı talebi',                3,    6,  NULL, 'orta',   'açık',    '2026-10-15 13:45', NULL),
    (13, 'Disk doluluğu %90''ı aştı',          2,    2,  6,    'yüksek', 'çözüldü', '2026-10-16 07:30', '2026-10-16 08:30'),
    (14, 'Zamanlanmış görev çalışmadı',        7,    1,  6,    'orta',   'çözüldü', '2026-10-16 09:20', '2026-10-17 09:20'),
    (15, 'İzleme uyarı eşiği güncellenecek',   10,   7,  4,    'düşük',  'açık',    '2026-10-16 11:00', NULL),
    (16, 'Web sunucusu 502 dönüyor',           2,    9,  2,    'kritik', 'çözüldü', '2026-10-17 18:05', '2026-10-17 19:00'),
    (17, 'Test ortamı kurulacak',              12,   5,  NULL, 'düşük',  'açık',    '2026-10-17 10:00', NULL),
    (18, 'Yazıcı sürücüsü güncellenecek',      NULL, 8,  NULL, 'düşük',  'açık',    '2026-10-18 09:00', NULL),
    (19, 'Veritabanı bakım penceresi',         4,    3,  10,   'orta',   'çözüldü', '2026-10-18 22:00', '2026-10-19 01:30'),
    (20, 'Disk doluluğu %90''ı aştı',          4,    10, 3,    'yüksek', 'açık',    '2026-10-19 06:50', NULL);

CREATE TABLE olcumler (
    sunucu_id INTEGER NOT NULL REFERENCES sunucular(id),
    zaman     TEXT NOT NULL,                         -- 'YYYY-AA-GG SS:DD'
    cpu       INTEGER NOT NULL,
    PRIMARY KEY (sunucu_id, zaman)
);

INSERT INTO olcumler (sunucu_id, zaman, cpu) VALUES
    (4, '2026-10-19 08:00', 62), (4, '2026-10-19 09:00', 75), (4, '2026-10-19 10:00', 91), (4, '2026-10-19 11:00', 88),
    (1, '2026-10-19 08:00', 40), (1, '2026-10-19 09:00', 58), (1, '2026-10-19 10:00', 72), (1, '2026-10-19 11:00', 69),
    (8, '2026-10-19 08:00', 70), (8, '2026-10-19 09:00', 71), (8, '2026-10-19 10:00', 84), (8, '2026-10-19 11:00', 90);

-- Öncelik başına hedef çözüm süresi (SPL yolunda lookup tablosu olarak da kullanılır)
CREATE TABLE sla (
    oncelik    TEXT PRIMARY KEY,
    hedef_saat INTEGER NOT NULL                       -- bilet en geç kaç saatte çözülmeli
);

INSERT INTO sla (oncelik, hedef_saat) VALUES
    ('kritik', 4), ('yüksek', 8), ('orta', 24), ('düşük', 72);

-- Gece bakım işlerinin günlük satırları: her iş çalışması başladı ... bitti satırları bırakır
CREATE TABLE isler (
    id      INTEGER PRIMARY KEY,
    zaman   TEXT NOT NULL,                            -- 'YYYY-AA-GG SS:DD'
    _time   INTEGER NOT NULL,                         -- aynı an, epoch saniyesi (Splunk'ın _time alanı gibi)
    sunucu  TEXT NOT NULL,
    is_adi  TEXT NOT NULL,
    calisma TEXT NOT NULL,                            -- çalışma kimliği: aynı çalışmanın satırları aynı kimliği taşır
    mesaj   TEXT NOT NULL
);

INSERT INTO isler (id, zaman, _time, sunucu, is_adi, calisma, mesaj) VALUES
(1 , '2026-10-17 01:00', 1792198800, 'yedek01', 'gece-yedek', 'Y17', 'başladı'),
    (2 , '2026-10-17 01:40', 1792201200, 'yedek01', 'gece-yedek', 'Y17', 'ilerleme %50'),
    (3 , '2026-10-17 02:00', 1792202400, 'db01', 'bakim', 'B17', 'başladı'),
    (4 , '2026-10-17 02:25', 1792203900, 'yedek01', 'gece-yedek', 'Y17', 'bitti'),
    (5 , '2026-10-17 02:35', 1792204500, 'db01', 'bakim', 'B17', 'bitti'),
    (6 , '2026-10-17 03:00', 1792206000, 'izleme01', 'log-dondur', 'L17', 'başladı'),
    (7 , '2026-10-17 03:04', 1792206240, 'izleme01', 'log-dondur', 'L17', 'bitti'),
    (8 , '2026-10-18 01:00', 1792285200, 'yedek01', 'gece-yedek', 'Y18', 'başladı'),
    (9 , '2026-10-18 01:50', 1792288200, 'yedek01', 'gece-yedek', 'Y18', 'ilerleme %50'),
    (10, '2026-10-18 03:20', 1792293600, 'yedek01', 'gece-yedek', 'Y18', 'bitti'),
    (11, '2026-10-18 06:00', 1792303200, 'web01', 'onbellek-isit', 'W18A', 'başladı'),
    (12, '2026-10-18 06:02', 1792303320, 'web01', 'onbellek-isit', 'W18A', 'bitti'),
    (13, '2026-10-18 06:30', 1792305000, 'web01', 'onbellek-isit', 'W18B', 'başladı'),
    (14, '2026-10-18 06:31', 1792305060, 'web01', 'onbellek-isit', 'W18B', 'bitti'),
    (15, '2026-10-19 01:00', 1792371600, 'yedek01', 'gece-yedek', 'Y19', 'başladı'),
    (16, '2026-10-19 01:45', 1792374300, 'yedek01', 'gece-yedek', 'Y19', 'ilerleme %50'),
    (17, '2026-10-19 02:00', 1792375200, 'db01', 'bakim', 'B19', 'başladı'),
    (18, '2026-10-19 02:20', 1792376400, 'db01', 'bakim', 'B19', 'uyarı: kilit bekleniyor'),
    (19, '2026-10-19 02:50', 1792378200, 'db01', 'bakim', 'B19', 'bitti');

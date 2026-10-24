package pafta.jpa;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import java.util.List;
import javax.sql.DataSource;
import org.springframework.context.annotation.*;
import org.springframework.data.jpa.repository.*;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.orm.jpa.*;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.stereotype.Service;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.*;
import org.springframework.transaction.support.TransactionSynchronizationManager;

@Entity
class Bilet {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) Long id;
    String baslik;
    String oncelik;
    String durum;
    protected Bilet() {}
    Bilet(String baslik, String oncelik, String durum) { this.baslik = baslik; this.oncelik = oncelik; this.durum = durum; }
    public String toString() { return id + ":" + baslik + "/" + oncelik + "/" + durum; }
}

interface BiletDeposu extends JpaRepository<Bilet, Long> {
    List<Bilet> findByDurumOrderByIdAsc(String durum);
    long countByOncelik(String oncelik);
    List<Bilet> findByOncelikInAndDurumNot(List<String> oncelikler, String durum);
    @Query("select b.baslik from Bilet b where b.durum = :durum and b.oncelik = 'kritik' order by b.id")
    List<String> kritikBasliklar(String durum);
    @Modifying @Query("update Bilet b set b.durum = 'kapalı' where b.oncelik = :oncelik")
    int topluKapat(String oncelik);
}

class OzelHata extends Exception { OzelHata(String m) { super(m); } }

@Service
class BiletServisi {
    final BiletDeposu depo;
    BiletServisi(BiletDeposu depo) { this.depo = depo; }
    static String islem() { return TransactionSynchronizationManager.isActualTransactionActive() ? "işlem var" : "işlem yok"; }

    @Transactional
    public void ikisiniEkle(boolean patlat) {
        depo.save(new Bilet("A", "orta", "açık"));
        if (patlat) throw new IllegalStateException("çalışma zamanı hatası");
        depo.save(new Bilet("B", "orta", "açık"));
    }

    @Transactional
    public void denetimliHata() throws OzelHata {
        depo.save(new Bilet("C", "düşük", "açık"));
        throw new OzelHata("denetimli");
    }

    @Transactional(rollbackFor = OzelHata.class)
    public void denetimliHataGeriAl() throws OzelHata {
        depo.save(new Bilet("D", "düşük", "açık"));
        throw new OzelHata("denetimli, rollbackFor");
    }

    public String disaridan() { return "dışarıdan çağrılan (işlemsiz yöntem): " + islem() + "; içeride çağrılan: " + iceriden(); }

    @Transactional
    public String iceriden() { return islem(); }

    @Transactional(readOnly = true)
    public String salt() { return islem() + ", salt okunur=" + TransactionSynchronizationManager.isCurrentTransactionReadOnly(); }

    @Transactional
    public int kapatVeSay(String oncelik) { return depo.topluKapat(oncelik); }
}

@Configuration
@EnableJpaRepositories(basePackageClasses = Ana.class)
@EnableTransactionManagement
@ComponentScan(basePackageClasses = Ana.class)
class Ayar {
    @Bean DataSource kaynak() { return new DriverManagerDataSource("jdbc:h2:mem:pafta;DB_CLOSE_DELAY=-1", "sa", ""); }
    @Bean LocalContainerEntityManagerFactoryBean entityManagerFactory(DataSource k) {
        var f = new LocalContainerEntityManagerFactoryBean();
        f.setDataSource(k);
        f.setManagedTypes(org.springframework.orm.jpa.persistenceunit.PersistenceManagedTypes.of(Bilet.class.getName()));
        f.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        f.getJpaPropertyMap().put("hibernate.hbm2ddl.auto", "create");
        return f;
    }
    @Bean PlatformTransactionManager transactionManager(jakarta.persistence.EntityManagerFactory e) { return new JpaTransactionManager(e); }
}

public class Ana {
    public static void main(String[] a) {
        try (var ctx = new AnnotationConfigApplicationContext(Ayar.class)) {
            var depo = ctx.getBean(BiletDeposu.class);
            var servis = ctx.getBean(BiletServisi.class);
            depo.saveAll(List.of(new Bilet("Disk dolu", "kritik", "açık"), new Bilet("Yama", "yüksek", "açık"),
                                 new Bilet("Yedek", "kritik", "kapalı"), new Bilet("DNS", "düşük", "açık"),
                                 new Bilet("502", "kritik", "açık")));
            System.out.println("türetilmiş: " + depo.findByDurumOrderByIdAsc("açık"));
            System.out.println("say kritik: " + depo.countByOncelik("kritik"));
            System.out.println("In/Not: " + depo.findByOncelikInAndDurumNot(List.of("kritik", "düşük"), "kapalı"));
            System.out.println("@Query: " + depo.kritikBasliklar("açık"));
            System.out.println("depo sınıfı proxy: " + java.lang.reflect.Proxy.isProxyClass(depo.getClass()));
            System.out.println("servis sınıfı: " + (servis.getClass() == BiletServisi.class ? "asıl sınıf" : "CGLIB alt sınıfı"));
            long once = depo.count();
            servis.ikisiniEkle(false);
            System.out.println("commit: " + once + " → " + depo.count());
            once = depo.count();
            try { servis.ikisiniEkle(true); } catch (IllegalStateException e) { System.out.println("yakalandı: " + e.getMessage()); }
            System.out.println("RuntimeException rollback: " + once + " → " + depo.count());
            once = depo.count();
            try { servis.denetimliHata(); } catch (OzelHata e) { System.out.println("yakalandı: " + e.getMessage()); }
            System.out.println("denetimli istisna: " + once + " → " + depo.count());
            once = depo.count();
            try { servis.denetimliHataGeriAl(); } catch (OzelHata e) { System.out.println("yakalandı: " + e.getMessage()); }
            System.out.println("rollbackFor: " + once + " → " + depo.count());
            System.out.println(servis.disaridan());
            System.out.println("doğrudan proxy üzerinden: " + servis.iceriden());
            System.out.println("readOnly: " + servis.salt());
            System.out.println("toplu kapat (@Modifying): " + servis.kapatVeSay("kritik"));
            try { depo.topluKapat("düşük"); System.out.println("işlemsiz @Modifying: geçti"); }
            catch (Exception e) { System.out.println("işlemsiz @Modifying: " + e.getClass().getSimpleName()); }
        }
    }
}

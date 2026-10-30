package pafta.template;

import freemarker.core.HTMLOutputFormat;
import freemarker.template.Configuration;
import freemarker.template.Template;
import java.io.StringWriter;
import java.util.Map;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;
import org.thymeleaf.templateresolver.StringTemplateResolver;

public class Ana {
    private static final String YUK = "<b>ad</b> & \"x\" 'y'";
    private static final Map<String, Object> MODEL = new RaporController().rapor(YUK);
    private static final TemplateEngine THYMELEAF = thymeleaf();

    public static void main(String[] args) throws Exception {
        System.out.println("yuk                 : " + YUK);
        System.out.println("--- Thymeleaf 3.1.3 / HTML kipi ---");
        thymeleafSatir("th:text=\"${ad}\"", Sablonlar.TEXT);
        thymeleafSatir("th:utext=\"${ad}\"", Sablonlar.UTEXT);
        thymeleafSatir("[[${ad}]]", Sablonlar.INLINE_TEXT);
        thymeleafSatir("[(${ad})]", Sablonlar.INLINE_UTEXT);
        thymeleafSatir("th:href=\"@{a(q=..)}\" ", Sablonlar.HREF);
        String js = thymeleaf(Sablonlar.JAVASCRIPT);
        System.out.println("JAVASCRIPT kipi     : " + js.replace("<script>", "").replace("</script>", ""));
        System.out.println("--- on isleme (alan = ${2*21}, duz = ayse) ---");
        thymeleafSatir("th:text=\"${alan}\"", Sablonlar.PRE_DATA);
        thymeleafSatir("th:text=\"__${alan}__\"", Sablonlar.PRE_CODE);
        thymeleafSatir("th:text=\"__${duz}__\"", Sablonlar.PRE_TOKEN);
        thymeleafSatir("th:text=\"'x' + __${duz}__\"", Sablonlar.PRE_CONCAT);
        thymeleafSatir("th:text=\"__${yok}__\"", Sablonlar.PRE_MISSING);
        System.out.println("--- FreeMarker 2.3.34 ---");
        freemarkerSatir("${ad}", Sablonlar.FM_VALUE, false);
        freemarkerSatir("${ad} + output HTML", Sablonlar.FM_VALUE, true);
        freemarkerSatir("${ad?html}", Sablonlar.FM_HTML, false);
        freemarkerSatir("${ad?html} + HTML", Sablonlar.FM_HTML, true);
        freemarkerSatir("${ad?no_esc} + HTML", Sablonlar.FM_NO_ESC, true);
        freemarkerSatir("${ad?no_esc} duz", Sablonlar.FM_NO_ESC, false);
    }

    private static TemplateEngine thymeleaf() {
        var resolver = new StringTemplateResolver();
        resolver.setTemplateMode("HTML");
        var engine = new TemplateEngine();
        engine.setTemplateResolver(resolver);
        return engine;
    }

    private static String thymeleaf(String template) {
        return THYMELEAF.process(template, new Context(null, MODEL));
    }

    private static void thymeleafSatir(String ad, String template) {
        System.out.printf("%-20s: %s%n", ad, thymeleaf(template));
    }

    private static void freemarkerSatir(String ad, String kaynak, boolean html) throws Exception {
        var ayar = new Configuration(Configuration.VERSION_2_3_34);
        if (html) ayar.setOutputFormat(HTMLOutputFormat.INSTANCE);
        try {
            var sablon = new Template("jv16", kaynak, ayar);
            var cikti = new StringWriter();
            sablon.process(MODEL, cikti);
            System.out.printf("%-20s: %s%n", ad, cikti);
        } catch (freemarker.core.ParseException e) {
            System.out.printf("%-20s: HATA %s%n", ad, e.getClass().getSimpleName());
        }
    }
}

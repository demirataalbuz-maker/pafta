package pafta.template;

import java.util.LinkedHashMap;
import java.util.Map;

/** İnceleme konusu controller parçası: istekten gelen değeri modele taşır. */
final class RaporController {
    Map<String, Object> rapor(String kullaniciGirdisi) {
        Map<String, Object> model = new LinkedHashMap<>();
        model.put("ad", kullaniciGirdisi);
        model.put("alan", "${2*21}");
        model.put("duz", "ayse");
        return model;
    }
}

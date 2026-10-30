package pafta.template;

/** JV16 kod incelemesinde kullanılan sabit şablon parçaları. */
final class Sablonlar {
    static final String TEXT = "<p th:text=\"${ad}\"></p>";
    static final String UTEXT = "<p th:utext=\"${ad}\"></p>";
    static final String INLINE_TEXT = "<p>[[${ad}]]</p>";
    static final String INLINE_UTEXT = "<p>[(${ad})]</p>";
    static final String HREF = "<a th:href=\"@{a(q=${ad})}\">l</a>";
    static final String JAVASCRIPT = "<script th:inline=\"javascript\">var s = [[${ad}]];</script>";
    static final String PRE_DATA = "<p th:text=\"${alan}\"></p>";
    static final String PRE_CODE = "<p th:text=\"__${alan}__\"></p>";
    static final String PRE_TOKEN = "<p th:text=\"__${duz}__\"></p>";
    static final String PRE_CONCAT = "<p th:text=\"'x' + __${duz}__\"></p>";
    static final String PRE_MISSING = "<p th:text=\"__${yok}__\"></p>";

    static final String FM_VALUE = "<p>${ad}</p>";
    static final String FM_HTML = "<p>${ad?html}</p>";
    static final String FM_NO_ESC = "<p>${ad?no_esc}</p>";

    private Sablonlar() {}
}

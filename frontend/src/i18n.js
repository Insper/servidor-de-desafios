import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import XHR from "i18next-xhr-backend";
import moment from "moment"

import translationEng from "./locales/en/translation.json";
import translationPt from "./locales/pt/translation.json";

i18n
  .use(XHR)
  .use(LanguageDetector)
  .init({
    // we init with resources
    resources: {
      en: {
        translations: translationEng
      },
      pt: {
        translations: translationPt
      }
    },
    fallbackLng: "pt",
    debug: true,

    // have a common namespace used around the full app
    ns: ["translations"],
    defaultNS: "translations",

    keySeparator: false, // we use content as keys

    interpolation: {
      escapeValue: false, // not needed for react!!
      formatSeparator: ",",
      format: function (value, format, lng) {
        if (format === 'uppercase') return value.toUpperCase();
        if (value instanceof Date) {
          if (format === "relative") return moment(value).fromNow();
          else return moment(value).format(format);
        }
        return value;
      }
    },

    react: {
      wait: true
    }
  });
i18n.on('languageChanged', function (lng) {
  moment.locale(lng);
});
i18n.changeLanguage("pt");  // Currently forcing pt-BR

export default i18n;

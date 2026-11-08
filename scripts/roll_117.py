# v1.1.7 changelog roll: catalog c0..c24 shift down + template relabel +
# bullet sync. Fail-fast: every edit in memory, asserts, THEN write files.
import json, re, collections, sys

CAT = "i18n/strings.json"
TPL = "templates/changelog/index.html"

NEW_DATE = {
    "en": "November 8, 2026", "de": "8. November 2026",
    "es": "8 de noviembre de 2026", "fr": "8 novembre 2026",
    "it": "8 novembre 2026", "pt": "8 de novembro de 2026",
    "nl": "8 november 2026", "pl": "8 listopada 2026",
    "ru": "8 ноября 2026", "uk": "8 листопада 2026",
    "tr": "8 Kasım 2026", "id": "8 November 2026",
    "ja": "2026年11月8日", "ko": "2026년 11월 8일", "zh": "2026年11月8日",
    "ar": "\u0668 \u0646\u0648\u0641\u0645\u0628\u0631 \u0662\u0660\u0662\u066c".replace("\u066c", "\u0666"),
    "hi": "8 \u0928\u0935\u0902\u092c\u0930 2026",
    "th": "8 \u0e1e.\u0e22. 2026",
    "vi": "8 th\u00e1ng 11, 2026",
}
SUMMARY = {
    "en": "Launch at Login finally does what it says on Mac.",
    "zh": "Mac 上的“登录时启动”现在真正生效。",
    "ja": "Mac の「ログイン時に起動」がついに正しく動作します。",
    "ko": "Mac의 '로그인 시 열기'가 이제 실제로 동작합니다.",
    "es": "“Abrir al iniciar sesión” por fin hace lo que promete en Mac.",
    "fr": "\u00ab Lancer \u00e0 la connexion \u00bb fait enfin ce qu'il promet sur Mac.",
    "de": "\"Beim Anmelden \u00f6ffnen\" tut auf dem Mac endlich, was es verspricht.",
    "pt": "\"Abrir ao iniciar sess\u00e3o\" finalmente faz o que promete no Mac.",
    "it": "\"Apri all'accesso\" finalmente fa ci\u00f2 che promette sul Mac.",
    "ru": "\u00ab\u0417\u0430\u043f\u0443\u0441\u043a\u0430\u0442\u044c \u043f\u0440\u0438 \u0432\u0445\u043e\u0434\u0435\u00bb \u043d\u0430 Mac \u043d\u0430\u043a\u043e\u043d\u0435\u0446 \u0440\u0430\u0431\u043e\u0442\u0430\u0435\u0442 \u043a\u0430\u043a \u043e\u0431\u0435\u0449\u0430\u043d\u043e.",
    "uk": "\u00ab\u0417\u0430\u043f\u0443\u0441\u043a\u0430\u0442\u0438 \u043f\u0440\u0438 \u0432\u0445\u043e\u0434\u0456\u00bb \u043d\u0430 Mac \u043d\u0430\u0440\u0435\u0448\u0442\u0456 \u043f\u0440\u0430\u0446\u044e\u0454 \u044f\u043a \u043e\u0431\u0456\u0446\u044f\u043d\u043e.",
    "nl": "\"Start bij inloggen\" doet op de Mac eindelijk wat het belooft.",
    "pl": "\"Uruchamiaj przy logowaniu\" wreszcie robi, co obiecuje na Macu.",
    "tr": "\"Giri\u015fte a\u00e7\" Mac'te sonunda s\u00f6z\u00fcn\u00fc tutuyor.",
    "id": "\"Buka saat login\" akhirnya benar-benar berfungsi di Mac.",
    "hi": "Mac \u092a\u0930 \u0932\u0949\u0917\u093f\u0928 \u092a\u0930 \u0932\u0949\u0928\u094d\u091a \u0906\u0916\u093f\u0930\u0915\u093e\u0930 \u0935\u0939\u0940 \u0915\u0930\u0924\u093e \u0939\u0948 \u091c\u094b \u0915\u0939\u0924\u093e \u0939\u0948\u0964",
    "ar": "\u00ab\u0627\u0644\u0641\u062a\u062d \u0639\u0646\u062f \u062a\u0633\u062c\u064a\u0644 \u0627\u0644\u062f\u062e\u0648\u0644\u00bb \u0639\u0644\u0649 Mac \u064a\u0642\u0648\u0645 \u0623\u062e\u064a\u0631\u064b\u0627 \u0628\u0645\u0627 \u064a\u0639\u062f\u0628\u0647.",
    "th": "\u0e40\u0e1b\u0e34\u0e14\u0e40\u0e21\u0e37\u0e48\u0e2d\u0e40\u0e02\u0e49\u0e32\u0e2a\u0e39\u0e48\u0e23\u0e30\u0e1a\u0e1a \u0e1a\u0e19 Mac \u0e17\u0e33\u0e15\u0e32\u0e21\u0e17\u0e35\u0e48\u0e1a\u0e2d\u0e01\u0e41\u0e25\u0e49\u0e27",
    "vi": "\u201cM\u1edf khi \u0111\u0103ng nh\u1eadp\u201d tr\u00ean Mac cu\u1ed1i c\u00f9ng \u0111\u00e3 ho\u1ea1t \u0111\u1ed9ng \u0111\u00fang nh\u01b0 h\u1ee9a.",
}
L1 = {
    "en": "Turning on Launch at Login now registers the login item right away, even when the menu bar app isn't running, so the app appears at your next login.",
    "zh": "打开“登录时启动”会立即完成登录项注册，即使菜单栏应用未在运行——下次登录时应用会正常出现。",
    "ja": "\u300c\u30ed\u30b0\u30a4\u30f3\u6642\u306b\u8d77\u52d5\u300d\u3092\u30aa\u30f3\u306b\u3059\u308b\u3068\u3001\u30e1\u30cb\u30e5\u30fc\u30d0\u30fc\u30a2\u30d7\u30ea\u304c\u8d77\u52d5\u3057\u3066\u3044\u306a\u304f\u3066\u3082\u30ed\u30b0\u30a4\u30f3\u9805\u76ee\u304c\u3059\u3050\u306b\u767b\u9332\u3055\u308c\u3001\u6b21\u56de\u306e\u30ed\u30b0\u30a4\u30f3\u6642\u306b\u30a2\u30d7\u30ea\u304c\u8d77\u52d5\u3057\u307e\u3059\u3002",
    "ko": "\u2018\ub85c\uadf8\uc778 \uc2dc \uc5f4\uae30\u2019\ub97c \ucf1c\uba74 \uba54\ub274 \ub9c9\ub300 \uc571\uc774 \uc2e4\ud589 \uc911\uc774 \uc544\ub2c8\uc5b4\ub3c4 \ub85c\uadf8\uc778 \ud56d\ubaa9\uc774 \uc989\uc2dc \ub4f1\ub85d\ub418\uc5b4 \ub2e4\uc74c \ub85c\uadf8\uc778 \uc2dc \uc571\uc774 \uc2e4\ud589\ub429\ub2c8\ub2e4.",
    "es": "Activarlo registra el elemento de inicio de sesi\u00f3n de inmediato, aunque la app de la barra de men\u00fa no est\u00e9 en ejecuci\u00f3n; la app aparecer\u00e1 en tu pr\u00f3ximo inicio de sesi\u00f3n.",
    "fr": "L'activer enregistre imm\u00e9diatement l'\u00e9l\u00e9ment de connexion, m\u00eame si l'app de la barre des menus n'est pas lanc\u00e9e\u00a0; l'app appara\u00eetra \u00e0 votre prochaine connexion.",
    "de": "Beim Aktivieren wird das Anmeldeelement sofort eingetragen, auch wenn die Men\u00fcleisten-App nicht l\u00e4uft \u2013 die App erscheint beim n\u00e4chsten Anmelden.",
    "pt": "Ativ\u00e1-lo registra o item de login imediatamente, mesmo com o app da barra de menus fechado, e o app abrir\u00e1 no pr\u00f3ximo login.",
    "it": "Attivandolo, l'elemento di accesso viene registrato subito, anche se l'app della barra dei menu non \u00e8 in esecuzione; l'app apparir\u00e0 al prossimo accesso.",
    "ru": "\u0412\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u0441\u0440\u0430\u0437\u0443 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u0443\u0435\u0442 \u044d\u043b\u0435\u043c\u0435\u043d\u0442 \u0430\u0432\u0442\u043e\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438, \u0434\u0430\u0436\u0435 \u0435\u0441\u043b\u0438 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u0432 \u0441\u0442\u0440\u043e\u043a\u0435 \u043c\u0435\u043d\u044e \u043d\u0435 \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u043e, \u2014 \u043e\u043d\u043e \u043f\u043e\u044f\u0432\u0438\u0442\u0441\u044f \u043f\u0440\u0438 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u043c \u0432\u0445\u043e\u0434\u0435.",
    "uk": "\u0423\u0432\u0456\u043c\u043a\u043d\u0435\u043d\u043d\u044f \u0432\u0456\u0434\u0440\u0430\u0437\u0443 \u0440\u0435\u0454\u0441\u0442\u0440\u0443\u0454 \u0435\u043b\u0435\u043c\u0435\u043d\u0442 \u0430\u0432\u0442\u043e\u0437\u0430\u043f\u0443\u0441\u043a\u0443, \u043d\u0430\u0432\u0456\u0442\u044c \u044f\u043a\u0449\u043e \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u0443 \u0432 \u043c\u0435\u043d\u044e-\u0431\u0430\u0440\u0456 \u043d\u0435 \u0437\u0430\u043f\u0443\u0449\u0435\u043d\u043e, \u2014 \u0432\u043e\u043d\u0430 \u0437'\u044f\u0432\u0438\u0442\u044c\u0441\u044f \u043f\u0456\u0434 \u043d\u0430\u0441\u0442\u0443\u043f\u043d\u043e\u0433\u043e \u0432\u0445\u043e\u0434\u0443.",
    "nl": "Inschakelen registreert het login-item meteen, zelfs als de menubalk-app niet draait; de app verschijnt bij je volgende login.",
    "pl": "W\u0142\u0105czenie natychmiast rejestruje element logowania, nawet gdy aplikacja paska menu nie dzia\u0142a \u2014 pojawi si\u0119 ona przy nast\u0119pnym logowaniu.",
    "tr": "A\u00e7t\u0131\u011f\u0131n\u0131zda giri\u015f \u00f6\u011fesi hemen kaydedilir \u2014 men\u00fc \u00e7ubu\u011fu uygulamas\u0131 \u00e7al\u0131\u015fm\u0131yorsa bile \u2014 ve uygulama bir sonraki giri\u015finizde belirir.",
    "id": "Mengaktifkannya langsung mendaftarkan item login, bahkan saat app bilah menu tidak berjalan, sehingga app muncul di login berikutnya.",
    "hi": "\u091a\u093e\u0932\u0942 \u0915\u0930\u0924\u0947 \u0939\u0940 \u0932\u0949\u0917\u093f\u0928 \u0906\u0907\u091f\u092e \u0924\u0941\u0930\u0902\u0924 \u092a\u0902\u091c\u0940\u0915\u0943\u0924 \u0939\u094b \u091c\u093e\u0924\u093e \u0939\u0948, \u091a\u093e\u0939\u0947 \u092e\u0947\u0928\u0942 \u092c\u093e\u0930 \u0910\u092a \u0928 \u091a\u0932 \u0930\u0939\u093e \u0939\u094b \u2014 \u0905\u0917\u0932\u0947 \u0932\u0949\u0917\u093f\u0928 \u092a\u0930 \u0910\u092a \u0926\u093f\u0916\u093e\u0908 \u0926\u0947\u0917\u093e\u0964",
    "ar": "\u0639\u0646\u062f \u0627\u0644\u062a\u0634\u063a\u064a\u0644\u060c \u064a\u064f\u0633\u062c\u0651\u0644 \u0639\u0646\u0635\u0631 \u062a\u0633\u062c\u064a\u0644 \u0627\u0644\u062f\u062e\u0648\u0644 \u0641\u0648\u0631\u064b\u0627 \u062d\u062a\u0649 \u0644\u0648 \u0644\u0645 \u064a\u0643\u0646 \u062a\u0637\u0628\u064a\u0642 \u0634\u0631\u064a\u0637 \u0627\u0644\u0642\u0648\u0627\u0626\u0645 \u0645\u0641\u062a\u0648\u062d\u064b\u0627\u060c \u0644\u064a\u0638\u0647\u0631 \u0627\u0644\u062a\u0637\u0628\u064a\u0642 \u0639\u0646\u062f \u062a\u0633\u062c\u064a\u0644 \u0627\u0644\u062f\u062e\u0648\u0644 \u0627\u0644\u0642\u0627\u062f\u0645.",
    "th": "\u0e40\u0e21\u0e37\u0e48\u0e2d\u0e40\u0e1b\u0e34\u0e14 \u0e23\u0e30\u0e1a\u0e1a\u0e08\u0e30\u0e25\u0e07\u0e17\u0e30\u0e40\u0e1a\u0e35\u0e22\u0e19 login item \u0e17\u0e31\u0e19\u0e17\u0e35 \u0e40\u0e21\u0e37\u0e48\u0e2d\u0e41\u0e01\u0e48\u0e07\u0e41\u0e2d\u0e1e\u0e1a\u0e19\u0e17\u0e30\u0e40\u0e1a\u0e32\u0e40\u0e21\u0e19\u0e39\u0e44\u0e21\u0e48\u0e44\u0e14\u0e49\u0e40\u0e23\u0e34\u0e48\u0e21\u0e27\u0e31\u0e25\u0e41\u0e25\u0e30 \u0e41\u0e2d\u0e1e\u0e08\u0e30\u0e1e\u0e1a\u0e21\u0e32\u0e40\u0e21\u0e37\u0e48\u0e2d\u0e40\u0e02\u0e49\u0e32\u0e2a\u0e39\u0e48\u0e04\u0e23\u0e31\u0e49\u0e07\u0e15\u0e48\u0e2d\u0e44\u0e1b",
    "vi": "Khi b\u1eadt, m\u1ee5c \u0111\u0103ng nh\u1eadp \u0111\u01b0\u1ee3c \u0111\u0103ng k\u00fd ngay l\u1eadp t\u1ee9c, k\u1ec3 c\u1ea3 khi \u1ee9ng d\u1ee5ng tr\u00ean thanh menu kh\u00f4ng ch\u1ea1y \u2014 \u1ee9ng d\u1ee5ng s\u1ebd xu\u1ea5t hi\u1ec7n \u1edf l\u1ea7n \u0111\u0103ng nh\u1eadp t\u1edbi.",
}
L2 = {
    "en": "The switch now mirrors what macOS actually has registered: if the registration isn't accepted, it flips back instead of staying falsely on.",
    "zh": "开关状态与系统实际注册保持一致：若注册未被系统接受，开关会自动复位，不再虚假地停在“开”。",
    "ja": "\u30b9\u30a4\u30c3\u30c1\u306fmacOS\u304c\u5b9f\u969b\u306b\u767b\u9332\u3057\u305f\u72b6\u614b\u3092\u53cd\u6620\u3057\u307e\u3059\u3002\u767b\u9332\u304c\u627f\u8a8d\u3055\u308c\u306a\u304b\u3063\u305f\u5834\u5408\u3001\u8aa4\u3063\u3066\u30aa\u30f3\u306e\u307e\u307e\u306b\u306a\u3089\u305a\u81ea\u52d5\u7684\u306b\u30aa\u30d5\u306b\u623b\u308a\u307e\u3059\u3002",
    "ko": "\uc2a4\uc704\uce58\ub294 macOS\uac00 \uc2e4\uc81c\ub85c \ub4f1\ub85d\ud55c \uc0c1\ud0dc\ub97c \ubc18\uc601\ud569\ub2c8\ub2e4. \ub4f1\ub85d\uc774 \uc2b9\uc778\ub418\uc9c0 \uc54a\uc73c\uba74 \uac70\uc9d3\uc73c\ub85c \ucf1c\uc9c4 \uc0c1\ud0dc\uac00 \ub0a8\uc544 \uc788\uc9c0 \uc54a\uace0 \uc2a4\uc2a4\ub85c \ub418\ub4e4\ub824\uac11\ub2c8\ub2e4.",
    "es": "El interruptor refleja lo que macOS tiene realmente registrado: si el registro no se acepta, vuelve a su lugar en vez de quedarse encendido.",
    "fr": "L'interrupteur refl\u00e8te ce que macOS a r\u00e9ellement enregistr\u00e9 : si l'enregistrement n'est pas accept\u00e9, il revient en arri\u00e8re au lieu de rester activ\u00e9.",
    "de": "Der Schalter zeigt den tats\u00e4chlich von macOS registrierten Zustand: Wird die Registrierung nicht angenommen, springt er zur\u00fcck, statt f\u00e4lschlich an zu bleiben.",
    "pt": "O bot\u00e3o reflete o que o macOS realmente registrou: se o registro n\u00e3o for aceito, ele volta ao lugar em vez de ficar ligado sem motivo.",
    "it": "L'interruttore riflette ci\u00f2 che macOS ha effettivamente registrato: se la registrazione non viene accettata, torna indietro invece di restare acceso.",
    "ru": "\u041f\u0435\u0440\u0435\u043a\u043b\u044e\u0447\u0430\u0442\u0435\u043b\u044c \u043e\u0442\u0440\u0430\u0436\u0430\u0435\u0442 \u0442\u043e, \u0447\u0442\u043e macOS \u0440\u0435\u0430\u043b\u044c\u043d\u043e \u0437\u0430\u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043b: \u0435\u0441\u043b\u0438 \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f \u043d\u0435 \u043f\u0440\u0438\u043d\u044f\u0442\u0430, \u043e\u043d \u0432\u043e\u0437\u0432\u0440\u0430\u0449\u0430\u0435\u0442\u0441\u044f \u043e\u0431\u0440\u0430\u0442\u043d\u043e, \u0430 \u043d\u0435 \u043e\u0441\u0442\u0430\u0451\u0442\u0441\u044f \u0432\u043a\u043b\u044e\u0447\u0451\u043d\u043d\u044b\u043c.",
    "uk": "\u041f\u0435\u0440\u0435\u043c\u0438\u043a\u0430\u0447 \u0432\u0456\u0434\u043e\u0431\u0440\u0430\u0436\u0430\u0454 \u0442\u0435, \u0449\u043e macOS \u043d\u0430\u0441\u043f\u0440\u0430\u0432\u0434\u0456 \u0437\u0430\u0440\u0435\u0454\u0441\u0442\u0440\u0443\u0432\u0430\u0432: \u044f\u043a\u0449\u043e \u0440\u0435\u0454\u0441\u0442\u0440\u0430\u0446\u0456\u044e \u043d\u0435 \u043f\u0440\u0438\u0439\u043d\u044f\u0442\u043e, \u0432\u0456\u043d \u043f\u043e\u0432\u0435\u0440\u0442\u0430\u0454\u0442\u044c\u0441\u044f, \u0430 \u043d\u0435 \u043b\u0438\u0448\u0430\u0454\u0442\u044c\u0441\u044f \u043f\u043e\u043c\u0438\u043b\u043a\u043e\u0432\u043e \u0443\u0432\u0456\u043c\u043a\u043d\u0435\u043d\u0438\u043c.",
    "nl": "De schakelaar toont wat macOS werkelijk heeft geregistreerd: wordt de registratie niet geaccepteerd, dan springt hij terug in plaats van vals aan te blijven.",
    "pl": "Prze\u0142\u0105cznik odzwierciedla to, co macOS faktycznie zarejestrowa\u0142: je\u015bli rejestracja nie zostanie przyj\u0119ta, wraca, zamiast pozosta\u0107 b\u0142\u0119dnie w\u0142\u0105czony.",
    "tr": "Anahtar, macOS'un ger\u00e7ekten kaydetti\u011fi durumu yans\u0131t\u0131r: kay\u0131t kabul edilmezse, yanl\u0131\u015f\u00e7a a\u00e7\u0131k kalmak yerine geri d\u00f6ner.",
    "id": "Sakelar kini mencerminkan apa yang benar-benar didaftarkan macOS: jika pendaftaran tidak diterima, sakelar kembali ke posisi semula alih-alih tetap menyala.",
    "hi": "\u0938\u094d\u0935\u093f\u091a \u0905\u092c macOS \u0926\u094d\u0935\u093e\u0930\u093e \u0935\u093e\u0938\u094d\u0924\u0935 \u092e\u0947\u0902 \u092a\u0902\u091c\u0940\u0915\u0943\u0924 \u0938\u094d\u0925\u093f\u0924\u093f \u0926\u093f\u0916\u093e\u0924\u093e \u0939\u0948: \u092a\u0902\u091c\u0940\u0915\u0930\u0923 \u0938\u094d\u0935\u0940\u0915\u093e\u0930 \u0928 \u0939\u094b\u0928\u0947 \u092a\u0930 \u0935\u0939 \u091d\u0942\u0920\u093e \u091a\u093e\u0932\u0942 \u0928\u0939\u0940\u0902 \u0930\u0939\u0924\u093e, \u092c\u0932\u094d\u0915\u093f \u0935\u093e\u092a\u0938 \u092c\u0902\u0926 \u0939\u094b \u091c\u093e\u0924\u093e \u0939\u0948\u0964",
    "ar": "\u064a\u0639\u0643\u0633 \u0627\u0644\u0645\u0641\u062a\u0627\u062d \u0645\u0627 \u0633\u062c\u0651\u0644\u062a\u0647 macOS \u0641\u0639\u0644\u064a\u064b\u0627: \u0625\u0646 \u0644\u0645 \u064a\u064f\u0642\u0628\u0644 \u0627\u0644\u062a\u0633\u062c\u064a\u0644\u060c \u064a\u0639\u0648\u062f \u0625\u0644\u0649 \u0648\u0636\u0639\u0647 \u0628\u062f\u0644\u0627\u064b \u0645\u0646 \u0623\u0646 \u064a\u0638\u0644 \u0645\u0641\u062a\u0648\u062d\u064b\u0627 \u062e\u0637\u0623\u064b.",
    "th": "\u0e2a\u0e27\u0e34\u0e15\u0e0a\u0e4c\u0e41\u0e2a\u0e14\u0e07\u0e2a\u0e16\u0e32\u0e19\u0e2d\u0e32\u0e19\u0e40\u0e01\u0e47\u0e19\u0e15\u0e32\u0e21\u0e17\u0e35\u0e48 macOS \u0e25\u0e07\u0e17\u0e30\u0e40\u0e1a\u0e35\u0e22\u0e19\u0e08\u0e23\u0e34\u0e07 \u0e2b\u0e32\u0e01\u0e44\u0e21\u0e48\u0e44\u0e14\u0e49\u0e23\u0e31\u0e1a\u0e40\u0e2a\u0e21\u0e2d\u0e19 \u0e21\u0e31\u0e19\u0e08\u0e30\u0e01\u0e25\u0e31\u0e1a\u0e01\u0e25\u0e31\u0e1a\u0e1b\u0e34\u0e14 \u0e41\u0e17\u0e19\u0e15\u0e34\u0e14\u0e04\u0e49\u0e32\u0e07\u0e40\u0e1b\u0e47\u0e19\u0e40\u0e1b\u0e34\u0e14",
    "vi": "C\u00f4ng t\u1eafc ph\u1ea3n \u00e1nh \u0111\u00fang nh\u1eefng g\u00ec macOS \u0111\u00e3 \u0111\u0103ng k\u00fd: n\u1ebfu \u0111\u0103ng k\u00fd kh\u00f4ng \u0111\u01b0\u1ee3c ch\u1ea5p nh\u1eadn, n\u00f3 t\u1ef1 tr\u1edf v\u1ec1 t\u1eaft thay v\u00ec v\u1eabn \u1edf tr\u1ea1ng th\u00e1i b\u1eadt.",
}
NEW_VERSION_LABEL = "v1.1.7"

doc = json.load(open(CAT))
strings = doc["strings"]
tpl = open(TPL).read()

# ---- dynamic MAX from catalog + template tokens -------------------------
MAX = max(int(m.group(1)) for k in strings for m in [re.match(r"^c(\d+)\.", k)] if m)
blocks = re.findall(r"\{\{(c\d+)\.summary\}\}", tpl)
assert blocks == [f"c{i}" for i in range(MAX + 1)], blocks
print(f"MAX={MAX}, blocks={len(blocks)}")

# ---- pre-state asserts ---------------------------------------------------
labels_old = re.findall(r'<div class="cl-version mono">([^<]+)', tpl)
assert labels_old[0] == "v1.1.6 ", labels_old[0]
assert tpl.count('<span class="cl-badge">') == 1
for i in range(MAX + 1):
    subs = {k[len(f"c{i}."):] for k in strings if k.startswith(f"c{i}.")}
    nli = len(re.findall(r"<li>\{\{c%d\.l\d+\}\}</li>" % i, tpl))
    assert "summary" in subs and "date" in subs
    assert nli == len([s for s in subs if re.fullmatch(r"l\d+", s)]), (i, nli, subs)

# ---- 1) catalog roll (order-preserving: update in place, delete stale,
#      append truly-new subkeys at the end) --------------------------------
def slot_subkeys(n):
    return sorted(k[len(f"c{n}."):] for k in strings if k.startswith(f"c{n}."))

new_strings = dict(strings)
for i in range(MAX, 0, -1):       # c{i} := c{i-1} whole subkey set
    old_subs = set(slot_subkeys(i))
    src_subs = slot_subkeys(i - 1)
    for sub in old_subs - set(src_subs):
        del new_strings[f"c{i}.{sub}"]
    for sub in src_subs:          # existing keys keep position; new append at end
        new_strings[f"c{i}.{sub}"] = strings[f"c{i-1}.{sub}"]
langs = list(strings["c0.summary"].keys())
assert len(langs) == 19, langs
for m in (NEW_DATE, SUMMARY, L1, L2):
    assert set(m.keys()) == set(langs), set(langs) ^ set(m.keys())
new_strings["c0.date"] = NEW_DATE
new_strings["c0.summary"] = SUMMARY
new_strings["c0.l1"] = L1
new_strings["c0.l2"] = L2

# new per-slot bullet counts from the ROLLED catalog
def new_bullets(n):
    return sorted(k for k in new_strings if re.fullmatch(rf"c{n}\.l\d+", k))
print("bullets:", [len(new_bullets(i)) for i in range(MAX + 1)])

# ---- 2) template relabel (shift labels; badge rides the new top) --------
# label of block i becomes old labels[i-1]; badge ONLY on block 0
labels_new = [NEW_VERSION_LABEL] + [l.strip() for l in labels_old[:MAX]]
def relabel(m, _i=[0]):
    i = _i[0]; _i[0] += 1
    inner = f'{labels_new[i]} <span class="cl-badge">{{{{c.latest}}}}</span>' if i == 0 else labels_new[i]
    return f'<div class="cl-version mono">{inner}</div>'
tpl2, n = re.subn(r'<div class="cl-version mono">(?:(?!</div>).)*</div>', relabel, tpl, count=MAX + 1)
assert n == MAX + 1, n
assert tpl2.count('<span class="cl-badge">') == 1

# ---- 3) bullet sync per block (rebuild every cl-list; removal before insertion) --
def rebuild_lists(t):
    out, pos, bi = [], 0, 0
    for m in re.finditer(r'<ul class="cl-list">[\s\S]*?</ul>', t):
        n_bullets = len(new_bullets(bi))
        tokens = "".join(f'\n              <li>{{{{c{bi}.l{j}}}}}</li>' for j in range(1, n_bullets + 1))
        out.append(t[pos:m.start()]); out.append(f'<ul class="cl-list">{tokens}\n            </ul>')
        pos = m.end(); bi += 1
    assert bi == MAX + 1, bi
    out.append(t[pos:])
    return "".join(out)

tpl2 = rebuild_lists(tpl2)

# ---- post-state asserts before writing anything --------------------------
for i in range(MAX + 1):
    nli = len(re.findall(r"<li>\{\{c%d\.l\d+\}\}</li>" % i, tpl2))
    assert nli == len(new_bullets(i)), (i, nli, len(new_bullets(i)))
    assert "{{c%d.date}}" % i in tpl2 and "{{c%d.summary}}" % i in tpl2
labs = re.findall(r'<div class="cl-version mono">([^<]+)', tpl2)
assert labs[0].strip() == NEW_VERSION_LABEL and labs[1].strip() == "v1.1.6", labs[:2]
assert tpl2.count('<span class="cl-badge">') == 1

# EN uniqueness of the new bullets vs the whole catalog (build.mjs lint)
en_texts = [v.get("en") for v in new_strings.values() if isinstance(v, dict)]
for t in (SUMMARY["en"], L1["en"], L2["en"]):
    assert en_texts.count(t) == 1, t

doc["strings"] = new_strings
with open(CAT, "w") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
    f.write("\n")
with open(TPL, "w") as f:
    f.write(tpl2)
print("ROLLED OK:", MAX + 1, "slots relabeled:", labs[:3], "bullets c0..c3:",
      [len(new_bullets(i)) for i in range(4)])

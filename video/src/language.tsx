import React from "react";
import type {Language} from "./types";

// Idioma do episódio, vindo de `SceneProps.language` (Scene.tsx): decide como os números aparecem (separadores do
// hodômetro, `locale` dos gráficos). Sem provedor, pt-BR.
const LanguageContext = React.createContext<Language>("pt-BR");

export const LanguageProvider = LanguageContext.Provider;
export const useLanguage = (): Language => React.useContext(LanguageContext);

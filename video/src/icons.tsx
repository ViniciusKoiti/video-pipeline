import React from "react";
import {LuBanknote, LuBuilding2, LuCircleDot, LuLandmark, LuUser, LuUsers} from "react-icons/lu";
import type {NodeKind} from "./types";

// Ícone de cada tipo de nó da rede (ADR 011, decisão 10): Lucide (licença ISC, ver ICONS.md), um por tipo.
// O roteiro escolhe só o tipo; ícone, cor e logo nunca vêm do roteiro.
export const NODE_ICONS: Record<NodeKind, React.ReactNode> = {
  person: <LuUser />,
  family: <LuUsers />,
  company: <LuBuilding2 />,
  bank: <LuBanknote />,
  government: <LuLandmark />,
  other: <LuCircleDot />,
};

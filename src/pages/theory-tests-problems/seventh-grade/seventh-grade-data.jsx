// src/pages/seventh-grade/seventh-grade-data.jsx

import React from 'react';
import { TTPTabContent } from '../theory-tests-problems';
import { Button } from 'antd';
import UnknownProblemsButton from './problems/UnknownProblemsButton';  // ← добавь импорт

// ==================== ТЕОРИЯ ====================
export const theory = [
    <TTPTabContent key="theory-1" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Изучить" path="theme1" />,
    <TTPTabContent key="theory-2" title="2. Углы и их измерение." buttonTitle="Изучить" path="theme2" />,
    <TTPTabContent key="theory-3" title="3. Треугольники." buttonTitle="Изучить" path="theme3" />,
];

// ==================== ТЕСТЫ ====================
export const tests = [
    <TTPTabContent key="test-1" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Сдать" grade="*" path="test1" />,
    <TTPTabContent key="test-2" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Сдано" grade="10" completed={true} path="test1" />,
    <TTPTabContent key="test-3" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Сдано" grade="7" completed={true} path="test1" />,
];

// ==================== ЗАДАЧИ ====================
export const problems = [
    <UnknownProblemsButton key="unknown-problems-button" />,
    // ←←← ВСЕ ОСТАЛЬНЫЕ ЗАДАЧИ НИЖЕ КНОПКИ
    <TTPTabContent key="problem-1" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-2" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-3" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-4" title="1. Прямая, луч, отрезок. Л: Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-5" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-6" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-7" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-8" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-9" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-10" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-11" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-12" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-13" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-14" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-15" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-16" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-17" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-18" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-19" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решено" completed={true} path="problem1" />,
    <TTPTabContent key="problem-20" title="1. Прямая, луч, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
    <TTPTabContent key="problem-21" title="1. Прямая, маска, отрезок. Ломаная." buttonTitle="Решить" path="problem1" />,
];

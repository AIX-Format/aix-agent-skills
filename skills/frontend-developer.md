# Frontend Developer — مهندس الواجهات

في عالم الواجهات الرقمية حيث يلتقي الجمال بالوظيفة، يأتي هذا المهارة كمعمار يبني الجسور بين الإنسان والآلة. يشيد الواجهات بإتقان، من React إلى Vue إلى الأصالة الخالصة، مزيناً إياها بالاستجابة والجاذبية. كفنان رقمي، يراعي أدق تفاصيل التفاعل ليجعل كل نقرة، كل تمريرة، كل نظرة تجربة لا تنسى.

## Purpose / الغرض

Build modern, responsive web interfaces using React, Vue, or vanilla HTML/CSS/JavaScript. Generates production-ready component code with responsive styling, accessibility (a11y), and cross-browser compatibility. Originally from GemClaw development skills.

## Constitutional Alignment / التوافق الدستوري

- **Golden Code Rule / قاعدة الكود الذهبية**: Leave code cleaner and more maintainable than you found it. Refactor as you go.
- **Accessibility / إمكانية الوصول**: Every interface must meet WCAG 2.1 AA minimum. aria attributes, keyboard navigation, and color contrast are non-negotiable.
- **Performance / الأداء**: Generated code must not regress Lighthouse scores; lazy loading and code splitting are applied where appropriate.
- **Separation of Concerns / فصل المسؤوليات**: Logic, styling, and markup remain in cleanly separated layers following component architecture best practices.

## Operational Flow / التدفق التشغيلي

1. Agent receives frontend requirement specifying layout, functionality, target framework, and design constraints.
2. Selects the appropriate framework (React with hooks, Vue 3 composition API, or vanilla) based on the project context.
3. Generates component code with state management, props interface, and lifecycle handling.
4. Applies responsive styling using the project's existing CSS methodology (Tailwind, CSS modules, styled-components, or plain CSS).
5. Runs lint checks and accessibility audit, then returns code with a rendered preview or description of the component's appearance and behavior.

## Failure Modes / أنماط الفشل

| Mode | Detection | Recovery |
|------|-----------|----------|
| Incomplete code | Lint errors or missing imports on build | Identify missing pieces and regenerate fixing all errors |
| Accessibility issues | a11y audit (axe-core) finds WCAG violations | Fix violations and re-run audit until clean |
| Style inconsistency | Generated CSS clashes with existing design tokens | Re-map to project's theme variables and regenerate |
| Framework mismatch | Code uses API not available in project's version | Detect version from package.json and adapt syntax |
| Runtime error | Component throws in sandbox test | Add error boundaries and fix the root cause with unit tests |

## References

- Related: `software-engineer.md` for full-stack integration with back-end services
- Related: `content-creator.md` for generating copy used in UI components

import type { NodePlopAPI, ActionType, PlopGeneratorConfig } from 'plop';
import * as fs from "fs";
import * as path from "path";

interface PlopAnswers {
  name: string;
  overwrite?: boolean;
  newName?: string;
}

export default function generator(plop: NodePlopAPI): void {
  const projectRoot = plop.getDestBasePath();

  plop.setGenerator("react-component", {
    description: "Adds a new react component",
    prompts: [
      {
        type: "input",
        name: "name",
        message: "What is the name of the component?",
      },
      {
        type: "confirm",
        name: "overwrite",
        message: "Component already exists. Do you want to overwrite it?",
        when: function(answers: any) {
          const componentPath = path.resolve(projectRoot, "packages/ui/src", `${answers.name}.tsx`);
          return fs.existsSync(componentPath);
        },
      },
      {
        type: "input",
        name: "newName",
        message: "Enter a new name for the component:",
        when: function(answers: any) {
          return !answers.overwrite && answers.overwrite !== undefined;
        },
      },
    ],
    actions: function(answers: any) {
      const actions: ActionType[] = [];
      const componentName = answers.newName || answers.name;
      const componentPath = path.resolve(projectRoot, "packages/ui/src", `${componentName}.tsx`);
      const indexPath = path.resolve(projectRoot, "packages/ui/src/index.ts");

      actions.push({
        type: "add",
        path: componentPath,
        templateFile: path.resolve(__dirname, "templates/component.hbs"),
        force: true,
      });

      actions.push({
        type: "append",
        path: indexPath,
        pattern: "// UI Component exports",
        template: `export { ${componentName} } from './${componentName}';`,
        skip: () => {
          if (!fs.existsSync(indexPath)) {
            fs.writeFileSync(indexPath, "// UI Component exports\n", "utf8");
            return false;
          }
          const fileContent = fs.readFileSync(indexPath, "utf8");
          return fileContent.includes(`export { ${componentName} }`);
        },
      });

      return actions;
    },
  } as PlopGeneratorConfig);
}


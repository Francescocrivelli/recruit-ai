declare module 'plop' {
  export interface NodePlopAPI {
    setGenerator(name: string, config: PlopGeneratorConfig): void;
    getDestBasePath(): string;
  }

  export interface PlopGeneratorConfig {
    description: string;
    prompts: Array<{
      type: string;
      name: string;
      message: string;
      when?: (answers: any) => boolean;
    }>;
    actions: (answers: any) => ActionType[];
  }

  export interface ActionType {
    type: string;
    path: string;
    templateFile?: string;
    force?: boolean;
    pattern?: string;
    template?: string;
    skip?: () => boolean | string;
  }
} 
interface Project {
  name: string;
  description: string;
  metrics: {
    stars?: number;
    forks?: number;
    contributions?: number;
  };
}

interface ProjectsMetricsProps {
  projects: Project[];
}

export default function ProjectsMetrics({ projects }: ProjectsMetricsProps) {
  return (
    <div className="mt-4 space-y-4">
      {projects.map((project) => (
        <div key={project.name} className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium text-lg">{project.name}</h4>
          <p className="text-gray-600 mt-2">{project.description}</p>
          <div className="flex gap-4 mt-2">
            {project.metrics.stars !== undefined && (
              <span className="text-sm text-gray-500">
                ⭐ {project.metrics.stars} stars
              </span>
            )}
            {project.metrics.forks !== undefined && (
              <span className="text-sm text-gray-500">
                🔄 {project.metrics.forks} forks
              </span>
            )}
            {project.metrics.contributions !== undefined && (
              <span className="text-sm text-gray-500">
                👨‍💻 {project.metrics.contributions} contributions
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
} 
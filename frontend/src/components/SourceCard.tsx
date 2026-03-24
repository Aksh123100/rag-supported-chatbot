import { SourceDocument } from '../services/api';

interface SourceCardProps {
  source: SourceDocument;
  index: number;
}

export default function SourceCard({ source, index }: SourceCardProps) {
  return (
    <div className="bg-gray-50 rounded-lg p-3 text-sm border border-gray-200">
      <div className="flex items-center gap-2 mb-2">
        <span className="bg-primary-100 text-primary-800 px-2 py-0.5 rounded text-xs font-medium">
          Source {index + 1}
        </span>
        {source.metadata.source && (
          <span className="text-gray-500 text-xs truncate">
            {String(source.metadata.source)}
          </span>
        )}
        <span className="ml-auto text-xs text-gray-400">
          {(source.score * 100).toFixed(1)}% match
        </span>
      </div>
      <p className="text-gray-600 text-xs leading-relaxed line-clamp-3">
        {source.content}
      </p>
      {source.metadata.category && (
        <span className="inline-block mt-2 bg-gray-200 text-gray-600 px-2 py-0.5 rounded text-xs">
          {String(source.metadata.category)}
        </span>
      )}
    </div>
  );
}
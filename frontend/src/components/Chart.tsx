export function EvolutionChart() {
  return (
    <div className="chart">
      <svg
        viewBox="0 0 640 190"
        role="img"
        aria-label="Evolução ilustrativa: domínio médio de 42 por cento em agosto para 67 por cento em outubro"
      >
        <defs>
          <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#2E9E73" stopOpacity=".18" />
            <stop offset="100%" stopColor="#2E9E73" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[35, 85, 135].map((y, i) => (
          <g key={y}>
            <line
              x1="40"
              x2="625"
              y1={y}
              y2={y}
              stroke="#E6E3DA"
              strokeDasharray="4 5"
            />
            <text x="0" y={y + 4} fill="#64697A" fontSize="11">
              {80 - i * 20}%
            </text>
          </g>
        ))}
        <path
          d="M45 130 C95 130 100 108 145 115 S210 100 255 102 S335 91 365 97 S435 77 475 80 S550 61 615 67.5 L615 160 L45 160Z"
          fill="url(#area)"
        />
        <path
          d="M45 130 C95 130 100 108 145 115 S210 100 255 102 S335 91 365 97 S435 77 475 80 S550 61 615 67.5"
          fill="none"
          stroke="#2E9E73"
          strokeWidth="3"
        />
        <circle
          cx="615"
          cy="67.5"
          r="5"
          fill="#2E9E73"
          stroke="white"
          strokeWidth="3"
        />
        {[
          "18 ago",
          "25 ago",
          "01 set",
          "08 set",
          "15 set",
          "22 set",
          "06 out",
        ].map((x, i) => (
          <text key={x} x={40 + i * 90} y="183" fill="#64697A" fontSize="11">
            {x}
          </text>
        ))}
      </svg>
    </div>
  );
}

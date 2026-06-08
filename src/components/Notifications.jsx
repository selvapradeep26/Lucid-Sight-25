export default function Notifications({ items }) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {items.map((n) => (
        <div
          key={n.id}
          className={`p-4 rounded-lg shadow-lg transition-opacity duration-300 ${
            n.type === "success" ? "bg-green-600" : "bg-red-600"
          }`}
        >
          <div className="flex items-center">
            <i className={`fas ${n.type === "success" ? "fa-check-circle" : "fa-exclamation-circle"} mr-2 text-white`}></i>
            <span className="text-white">{n.message}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function MovieCard({ title }) {
  return (
    <div className="bg-white shadow-md rounded-xl p-4 hover:shadow-xl transition transform hover:scale-105 duration-200">
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
    </div>
  );
}

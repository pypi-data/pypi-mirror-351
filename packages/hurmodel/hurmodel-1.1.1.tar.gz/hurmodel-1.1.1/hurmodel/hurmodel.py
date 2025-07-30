# THIS IS AN EXTENSION NETWORK OF THE SKILLS OF THE HURNET ARTIFICIAL NEURAL NETWORK
# The HurModel (Hur of HurNet and Model of language model) is a sophisticated artificial neural network computational algorithm that proposes a new architecture for language models based on Transformers.
# This architecture uses aspects already known from Transformers applied to GPT models, such as normalizers, tokenizers, embeddings and attention mechanisms,
# but adds new concepts such as intelligent initialization of weights using layers of the HurNet network, insertion of auxiliary HurNet layers and use of HurNet networks in the final adjustment of weights.
# As an integral part of the architecture, HurModel models do not require hyperparameter configurations, since this can be done completely autonomously without developer intervention,
# allowing the programmer to focus only on the data that is the most important part of the model. All these features make the HurModel language model architecture superior to the already known GPT models.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
class HurModel:
    def __init__(self, embedding_dim=None, block_size=None, batch_size=None, number_heads=None, number_layers=None, dropout=None, learning_rate=None, eval_interval=None, epochs=None):
        import warnings
        from torch import cuda, device, backends, tensor, triu, ones as t_ones, int64, no_grad, multinomial, cat, optim, zeros, save, load
        from torch.utils.data import Dataset, DataLoader
        from torch.nn import Module, Parameter, Dropout, Embedding, TransformerDecoder, TransformerDecoderLayer, Linear, functional as Function
        from math import sqrt
        from re import sub
        from tiktoken import get_encoding
        from time import sleep, time
        from json import load as json_load
        from tqdm import tqdm
        from os import path as os_path, makedirs as os_makedirs
        from statistics import mean
        warnings.filterwarnings('ignore')
        if cuda.is_available(): local_device = device('cuda')
        elif backends.mps.is_available(): local_device = device('mps')
        else: local_device = device('cpu')
        self.__device = local_device
        self.__Dataset = Dataset
        self.__Module = Module
        self.__Parameter = Parameter
        self.__tensor = tensor
        self.__Dropout = Dropout
        self.__Embedding = Embedding
        self.__TransformerDecoder = TransformerDecoder
        self.__TransformerDecoderLayer = TransformerDecoderLayer
        self.__triu = triu
        self.__ones = t_ones
        self.__Linear = Linear
        self.__sqrt = sqrt
        self.__sub = sub
        self.__get_encoding = get_encoding
        self.__sleep = sleep
        self.__int64 = int64
        self.__no_grad = no_grad
        self.__Function = Function
        self.__multinomial = multinomial
        self.__cat = cat
        self.__cuda = cuda
        self.__time = time
        self.__json_load = json_load
        self.__DataLoader = DataLoader
        self.__optim = optim
        self.__zeros = zeros
        self.__tqdm = tqdm
        self.__os_path = os_path
        self.__os_makedirs = os_makedirs
        self.__mean = mean
        self.__save = save
        self.__load = load
        self.__block_size = max((1, int(block_size))) if block_size is not None else None
        self.__batch_size = max((1, int(batch_size))) if batch_size is not None else None
        self.__embedding_dim = max((1, int(embedding_dim))) if embedding_dim is not None else None
        self.__number_heads = max((1, int(number_heads))) if number_heads is not None else None
        self.__number_layers = max((1, int(number_layers))) if number_layers is not None else None
        self.__epochs = max((1, int(epochs))) if epochs is not None else None
        self.__fine_tuning = []
        self.__interval = None
        self.__precision = 0.5
        self.__tokenizer = 'gpt'
        self.__model = None
        self.__encode = None
        self.__decode = None
        self.__end_tag = None
        self.__string = ''
        self.__vocab_size = 0
        self.__char_to_idx = {}
        self.__idx_to_char = {}
        self.__optimizer = None
        self.__learning_rate = max((0, float(learning_rate))) if type(learning_rate) in (bool, int, float) else 3e-4
        self.__eval_interval = max((1, int(eval_interval))) if type(eval_interval) in (bool, int, float) else None
        self.__train = False
        self.__precisions = []
        self.dropout = max((0, float(dropout))) if type(dropout) in (bool, int, float) else 0.1
        self.parameters_number = 0
        class HurNetTorch(Module):
            def __init__(self, input_dim=(1,), output_dim=(1,), activation='linear', interaction=True, bias=0.0, device='cuda'):
                super().__init__()
                from torch import randn, prod, sigmoid, tanh, relu, linalg
                self.__interaction = interaction
                self.__activation = activation.lower()
                self.__bias = bias
                self.__device = device
                self.__prod = prod
                self.__sigmoid = sigmoid
                self.__tanh = tanh
                self.__relu = relu
                self.__linalg = linalg
                self.weights = Parameter(randn(input_dim + 2, output_dim, device=device))
            def __add_features(self, x=[]):
                if self.__interaction: interaction = self.__prod(x, dim=1, keepdim=True)
                else: interaction = zeros((x.shape[0], 1), device=self.__device)
                ones = t_ones((x.shape[0], 1), device=self.__device)
                return cat([x, interaction, ones], dim=1)
            def __apply_activation(self, x=[]):
                activation_functions = {'linear': lambda x: x, 'sigmoid': self.__sigmoid, 'tanh': self.__tanh, 'relu': self.__relu}
                return activation_functions.get(self.__activation, lambda x: x)(x)
            def train_layer(self, x=[], y=[]):
                if not x.is_cuda: x = x.to(self.__device)
                if not y.is_cuda: y = y.to(self.__device)
                x_augmented = self.__add_features(x)
                x_augmented_transpose = x_augmented.T
                if self.__interaction: self.weights.data = (self.__linalg.pinv(x_augmented_transpose @ x_augmented) @ (x_augmented_transpose @ y) + self.__bias)
                else: self.weights.data = (self.__linalg.pinv(x_augmented) @ y + self.__bias)
            def forward(self, x=[]):
                if not x.is_cuda: x = x.to(self.__device)
                x_augmented = self.__add_features(x)
                y_predicted = x_augmented @ self.weights
                return self.__apply_activation(y_predicted)
        class TextDataset(self.__Dataset):
            def __init__(self, data=[], block_size=0): self.__data, self.__block_size = data, block_size
            def __len__(self): return max(0, len(self.__data) - self.__block_size)
            def __getitem__(self, index=0): return self.__data[index:index + self.__block_size], self.__data[index + 1:index + self.__block_size + 1]
        class TransformerWithHurNet(self.__Module):
            def __init__(self, outer=None, vocab_size=0, embedding_dim=0, number_heads=0, number_layers=0, dropout=None, block_size=0, device='cuda'):
                super().__init__()
                self.__outer = outer
                self.__block_size = block_size
                self.positional_encoding = outer._HurModel__Parameter(outer._HurModel__tensor([]).new_zeros(1, block_size, embedding_dim))
                self.dropout = outer._HurModel__Dropout(dropout)
                self.embedding = outer._HurModel__Embedding(vocab_size, embedding_dim)
                self.multi_head_attention = outer._HurModel__TransformerDecoder(outer._HurModel__TransformerDecoderLayer(d_model=embedding_dim, nhead=number_heads, dropout=dropout, batch_first=True), num_layers=number_layers)
                self.hurnet_layer = HurNetTorch(embedding_dim, vocab_size, activation='linear', interaction=True, device=device)
            def forward(self, input_tensor=[]):
                batch_size, sequence_length = input_tensor.size()
                positions = self.positional_encoding[:, :sequence_length, :].to(input_tensor.device)
                outer = self.__outer
                input_embedding = self.dropout(self.embedding(input_tensor) + positions)
                masked_multi_head_attention = outer._HurModel__triu(outer._HurModel__ones(sequence_length, sequence_length, device=input_tensor.device) * float('-inf'), diagonal=1)
                output_embedding = self.multi_head_attention(input_embedding, memory=input_embedding, tgt_mask=masked_multi_head_attention)
                return self.hurnet_layer(output_embedding.reshape(-1, output_embedding.size(-1))).view(batch_size, sequence_length, -1)
        class TransformerWithoutHurNet(self.__Module):
            def __init__(self, outer=None, vocab_size=0, embedding_dim=0, number_heads=0, number_layers=0, dropout=None, block_size=0):
                super().__init__()
                self.__outer = outer
                self.__block_size = block_size
                self.positional_encoding = outer._HurModel__Parameter(outer._HurModel__tensor([]).new_zeros(1, block_size, embedding_dim))
                self.dropout = outer._HurModel__Dropout(dropout)
                self.embedding = outer._HurModel__Embedding(vocab_size, embedding_dim)
                self.multi_head_attention = outer._HurModel__TransformerDecoder(outer._HurModel__TransformerDecoderLayer(d_model=embedding_dim, nhead=number_heads, dropout=dropout, batch_first=True), num_layers=number_layers)
                self.__add_and_norm = outer._HurModel__Linear(embedding_dim, vocab_size)
                self.output_layer = self.__add_and_norm
            def forward(self, input_tensor=[]):
                batch_size, sequence_length = input_tensor.size()
                positions = self.positional_encoding[:, :sequence_length, :].to(input_tensor.device)
                outer = self.__outer
                input_embedding = self.dropout(self.embedding(input_tensor) + positions)
                masked_multi_head_attention = outer._HurModel__triu(outer._HurModel__ones(sequence_length, sequence_length, device=input_tensor.device) * float('-inf'), diagonal=1)
                output_embedding = self.multi_head_attention(input_embedding, memory=input_embedding, tgt_mask=masked_multi_head_attention)
                return self.__add_and_norm(output_embedding)
        self.__HurNetTorch = HurNetTorch
        self.__TextDataset = TextDataset
        self.__TransformerWithHurNet = TransformerWithHurNet
        self.__TransformerWithoutHurNet = TransformerWithoutHurNet
    def __adjust_hyperparameters_sapi(self, dataset_size=0, context_window=None):
        if self.__block_size is None:
            if context_window is not None: self.__block_size = max(8, int(context_window))
            else: self.__block_size = min(1024, max(8, int(0.7 * (dataset_size ** 0.3) + 0.5 * (dataset_size ** 0.5))))
        if self.__batch_size is None: self.__batch_size = min(128, max(4, int(self.__sqrt(dataset_size * self.__block_size) / 8)))
        if self.__embedding_dim is None: self.__embedding_dim = min(512, max(128, int(128 * (dataset_size * self.__block_size) ** 0.15)))
        if self.__number_heads is None: self.__number_heads = min(16, max(4, int((dataset_size ** 0.2 + self.__block_size ** 0.2) / 1.5)))
        if self.__embedding_dim % self.__number_heads != 0: self.__embedding_dim += (self.__number_heads - (self.__embedding_dim % self.__number_heads))
        if self.__number_layers is None: self.__number_layers = min(8, max(2, int((dataset_size ** 0.15 + self.__block_size ** 0.15) / 2)))
        if self.__epochs is None: self.__epochs = min(300, max(50, int(20000 / dataset_size + 200 / self.__block_size + 20)))
    def __adjust_hyperparameters_gpt(self, dataset_size=0, context_window=None):
        if self.__block_size is None:
            if context_window is not None: self.__block_size = max(8, int(context_window))
            else: self.__block_size = min(1024, max(8, int(0.5 * (dataset_size ** 0.3) + 0.3 * (dataset_size ** 0.5))))
        if self.__batch_size is None: self.__batch_size = min(64, max(4, int(self.__sqrt(dataset_size * self.__block_size) / 10)))
        if self.__embedding_dim is None: self.__embedding_dim = min(256, max(64, int(64 * (dataset_size * self.__block_size) ** 0.1)))
        if self.__number_heads is None: self.__number_heads = min(8, max(2, int((dataset_size ** 0.2 + self.__block_size ** 0.2) / 2)))
        if self.__embedding_dim % self.__number_heads != 0: self.__embedding_dim += (self.__number_heads - (self.__embedding_dim % self.__number_heads))
        if self.__number_layers is None: self.__number_layers = min(4, max(1, int((dataset_size ** 0.15 + self.__block_size ** 0.15) / 3)))
        if self.__epochs is None: self.__epochs = min(100, max(10, int(10000 / dataset_size + 100 / self.__block_size + 10)))
    def __normalize_text(self, text=''):
        normalized = text.lower()
        normalized = self.__sub(r'[àáâãäå]', 'a', normalized)
        normalized = self.__sub(r'[èéêë]', 'e', normalized)
        normalized = self.__sub(r'[ìíîï]', 'i', normalized)
        normalized = self.__sub(r'[òóôõö]', 'o', normalized)
        normalized = self.__sub(r'[ùúûü]', 'u', normalized)
        normalized = self.__sub(r'[ç]', 'c', normalized)
        normalized = self.__sub(r'[ñ]', 'n', normalized)
        normalized = self.__sub(r'[^a-z0-9\s+\-*/=()]', '', normalized)
        tokens = normalized.split()
        processed_tokens = [token[:-5] if len(token) > 5 else token for token in tokens]
        return ' '.join(processed_tokens)
    def __generate_tokens_x(self, prompt='', max_tokens=500, temperature=0.5, top_k=50, top_p=0.9, end_tag=None):
        if len(self.__fine_tuning) > 0 and self.__interval is not None:
            inputs = self.__get_encoding('cl100k_base').encode(self.__normalize_text(text=prompt))
            inputs_length = len(inputs)
            def find_closest(number=0, number_list=[]):
                closest = number_list[0]
                minimum_difference = abs(number - closest)
                for numeric_item in number_list:
                    current_difference = abs(number - numeric_item)
                    if current_difference < minimum_difference: minimum_difference, closest = current_difference, numeric_item
                return closest
            best_score, best_index = 0, 0
            for index, fine_tuning in enumerate(self.__fine_tuning):
                embedding = fine_tuning['embedding'] if 'embedding' in fine_tuning else fine_tuning[list(fine_tuning.keys())[0]]
                if inputs == embedding:
                    best_score, best_index = 1.0, index
                    break
                tokens_x, tokens_y, score = (embedding, inputs, 0) if len(embedding) < inputs_length else (inputs, embedding, 0)
                for token in tokens_x:
                    if token in tokens_y: score += 1
                    else:
                        closest = find_closest(number=token, number_list=tokens_y)
                        score += abs(token-closest)/max((token, closest))
                score /= max((1, len(embedding)))
                if score > best_score: best_score, best_index = score, index
            if best_score >= self.__precision:
                outputs = self.__fine_tuning[best_index]['answer']
                if end_tag is not None: outputs = outputs.replace(str(end_tag), '')
                def split_into_4_char_chunks(input_string=''): return [input_string[index:index+4] for index in range(0, len(input_string), 4)]
                output_tokens = outputs if self.__tokenizer == 'sapi' else split_into_4_char_chunks(input_string=outputs)
                for token in output_tokens:
                    yield token
                    if self.__interval is not None: self.__sleep(self.__interval)
                return ''
        self.__model.eval()
        def get_last_n_tokens(text='', n=0):
            if self.__tokenizer == 'sapi': return text[-n:]
            else:
                encoding = self.__get_encoding('gpt2')
                tokens = encoding.encode(text)
                last_n_tokens = tokens[-n:]
                truncated_text = encoding.decode(last_n_tokens)
                return truncated_text
        encoded_prompt = self.__encode(get_last_n_tokens(text=prompt, n=self.__block_size))
        input_tensor = self.__tensor(encoded_prompt, dtype=self.__int64).unsqueeze(0).to(self.__device)
        tokens_generated, tokens_union, terminators, gpt_tokenizer = 0, '', ('.', '\n', '!', ';', '?'), self.__tokenizer == 'gpt'
        def closing(tokens_union='', end_tag='', terminators=[]):
            tokens_union_limit = len(tokens_union)
            for terminator in terminators:
                index = tokens_union.rfind(terminator)
                if (index >= 0) and ((index + 1) < tokens_union_limit):
                    after_termination = tokens_union[index+1:]
                    if len(after_termination) > 0 and after_termination in end_tag: return True
            return False
        with self.__no_grad():
            while True:
                conditioned_input = input_tensor[:, -self.__block_size:] if input_tensor.size(1) > self.__block_size else input_tensor
                logistics = self.__model(conditioned_input)
                logistics = logistics[:, -1, :] / temperature
                sorted_logistics, sorted_indexes = logistics.sort(descending=True)
                vocab_size = logistics.size(-1)
                if top_k is None or top_k <= 0 or top_k > vocab_size: top_k = vocab_size
                top_k_logistics, top_k_indexes = sorted_logistics[:top_k], sorted_indexes[:top_k]
                cumulative_probabilities = self.__Function.softmax(top_k_logistics, dim=-1).cumsum(dim=-1)
                mask = cumulative_probabilities <= top_p
                if mask.sum() == 0: mask[0] = True
                filtered_logistics, filtered_indexes = top_k_logistics[mask], top_k_indexes[mask]
                output_probabilities = self.__Function.softmax(filtered_logistics, dim=-1)
                next_token = self.__multinomial(output_probabilities, num_samples=1)
                next_token = filtered_indexes[next_token].unsqueeze(0)
                input_tensor = self.__cat((input_tensor, next_token), dim=1)
                shifted_right = next_token.item()
                decoded_token = self.__decode([shifted_right])
                if tokens_generated == 0 and '\n' in decoded_token: continue
                tokens_generated += 1
                tokens_union += decoded_token
                if end_tag is not None and closing(tokens_union=tokens_union, end_tag=end_tag, terminators=terminators):
                    if gpt_tokenizer:
                        for terminator in terminators:
                            if terminator in decoded_token:
                                decoded_token = decoded_token.split(terminator)[0]+terminator
                                yield decoded_token
                                break
                    break
                elif (end_tag is not None and gpt_tokenizer) and (decoded_token in end_tag or decoded_token.endswith(end_tag) or tokens_union.endswith(end_tag)): break
                else: yield decoded_token
                if (tokens_generated >= max_tokens and decoded_token[-1] in terminators) or (tokens_generated >= (max_tokens * 2)): break
        self.__cuda.empty_cache()
    def __adjust_hyperparameters(self, dataset_size=0, context_window=None, tokenizer='gpt'):
        if tokenizer == 'sapi': self.__adjust_hyperparameters_sapi(dataset_size, context_window=None)
        else: self.__adjust_hyperparameters_gpt(dataset_size, context_window=None)
    def __identify_best_activation_function(self, x=[], y=[], interaction=True, candidate_activations=None):
        if candidate_activations is None: candidate_activations = ('linear', 'sigmoid', 'tanh', 'relu')
        input_features = x.size(-1)
        output_features = y.size(-1)
        best_loss = float('inf')
        best_activation = candidate_activations[0]
        for activation in candidate_activations:
            temporary_layer = self.__HurNetTorch(input_dim=input_features, output_dim=output_features, activation=activation, interaction=interaction, device=self.__device)
            x_flat, y_flat = x.reshape(-1, input_features), y.reshape(-1, output_features)
            temporary_layer.train_layer(x=x_flat, y=y_flat)
            predictions = temporary_layer(x)
            loss = self.__Function.mse_loss(predictions, y)
            if loss.item() < best_loss: best_loss, best_activation = loss.item(), activation
        return best_activation
    def __identify_best_bias(self, x=[], y=[], best_activation='linear', interaction=True):
        input_features, output_features = x.size(-1), y.size(-1)
        x_flat, y_flat = x.reshape(-1, input_features), y.reshape(-1, output_features)
        current_bias = 0.0
        temporary_layer = self.__HurNetTorch(input_dim=input_features, output_dim=output_features, activation=best_activation, interaction=interaction, bias=current_bias, device=self.__device)
        temporary_layer.train_layer(x=x_flat, y=y_flat)
        predictions, step = temporary_layer(x), 0.1
        best_loss = self.__Function.mse_loss(predictions, y).item()
        for _ in range(30):
            improved = False
            for direction in (-1, 1):
                candidate_bias = current_bias + direction * step
                temporary_layer = self.__HurNetTorch(input_dim=input_features, output_dim=output_features, activation=best_activation, interaction=interaction, bias=candidate_bias, device=self.__device)
                temporary_layer.train_layer(x=x_flat, y=y_flat)
                predictions = temporary_layer(x)
                loss = self.__Function.mse_loss(predictions, y).item()
                if loss < best_loss: best_loss, improved, current_bias = loss, True, candidate_bias                    
            if not improved:
                step /= 2
                if step < 1e-4: break
        return current_bias
    def __identify_best_interaction(self, x=[], y=[], best_activation='linear', best_bias=0.0):
        input_features, output_features = x.size(-1), y.size(-1)
        x_flat, y_flat = x.reshape(-1, input_features), y.reshape(-1, output_features)
        best_loss, best_interaction = float('inf'), False
        for candidate in (True, False):
            temporary_layer = self.__HurNetTorch(input_dim=input_features, output_dim=output_features, activation=best_activation, interaction=candidate, bias=best_bias, device=self.__device)
            temporary_layer.train_layer(x=x_flat, y=y_flat)
            predictions = temporary_layer(x)
            loss = self.__Function.mse_loss(predictions, y).item()
            if loss < best_loss: best_loss, best_interaction = loss, candidate
        return best_interaction
    def __format_numbers(self, data_number=0, is_tokens=False):
        if data_number < 1_000: return data_number if is_tokens else f'{data_number}U'
        elif data_number < 1_000_000: return f'{data_number // 1_000}K'
        elif data_number < 1_000_000_000: return f'{data_number // 1_000_000}M'
        elif data_number < 1_000_000_000_000: return f'{data_number // 1_000_000_000}B'
        else: return f'{data_number // 1_000_000_000_000}T'
    def __compute_loss(self, loader=[]):
        if len(loader) == 0: return float('inf')
        self.__model.eval()
        total_loss = 0
        with self.__no_grad():
            for input_batch, target_batch in loader:
                input_batch, target_batch = input_batch.to(self.__device), target_batch.to(self.__device)
                logistics = self.__model(input_batch)
                loss = self.__Function.cross_entropy(logistics.reshape(-1, logistics.size(-1)), target_batch.reshape(-1))
                total_loss += loss.item()
        self.__cuda.empty_cache()
        return total_loss / len(loader)
    def __generate_tokens(self, prompt='', max_tokens=500, temperature=0.5, top_k=50, top_p=0.9, end_tag=None):
        if len(prompt) < 1: prompt = '?'
        if self.__interval is None:
            from psutil import virtual_memory
            from torch import cuda, backends
            def estimate_token_interval():
                if cuda.is_available(): total_memory, base_time = cuda.get_device_properties(0).total_memory / 1e9, 0.01
                elif backends.mps.is_available(): total_memory, base_time = virtual_memory().total / 1e9, 0.025
                else: total_memory, base_time = virtual_memory().total / 1e9, 0.05
                if total_memory < 4: memory_factor = 2.0
                elif total_memory < 8: memory_factor = 1.5
                elif total_memory < 16: memory_factor = 1.2
                else: memory_factor = 1.0
                return round(base_time * memory_factor, 4) / 2
            self.__interval = estimate_token_interval()
        return self.__generate_tokens_x(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p, end_tag=end_tag)
    def train(self, dataset_path='', string='', precision=1.0, tokenizer='gpt', context_window=None, hurnet_initializer=True, hurnet_layer=False, hurnet_fit=False, end_tag=None, validate=0.0, progress=True):
        try:
            training_metrics = {'val_loss': 0.0, 'loss': 0.0, 'generalization_rate': 0.0, 'precision': 0.0}
            dataset_path = str(dataset_path).strip()
            string = str(string).strip()
            precision = min((1.0, max((0.0, float(precision))))) if type(precision) in (bool, int, float) else 1.0
            tokenizer = str(tokenizer).lower().strip()
            if context_window is not None: context_window = max((8, int(context_window))) if type(context_window) in (bool, int, float) else None
            hurnet_initializer = bool(hurnet_initializer) if type(hurnet_initializer) in (bool, int, float) else True
            hurnet_layer = original_hurtnet_layer = bool(hurnet_layer) if type(hurnet_layer) in (bool, int, float) else False
            hurnet_fit = original_hurnet_fit = bool(hurnet_fit) if type(hurnet_fit) in (bool, int, float) else False
            if end_tag is not None and self.__end_tag is None: self.__end_tag = str(end_tag)
            validate = min((1.0, max((0.0, float(validate))))) if type(validate) in (bool, int, float) else 0.0
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if tokenizer not in ('sapi', 'gpt'): tokenizer = 'gpt'
            self.__string = str(self.__string+'\n\n'+string).strip()
            if hurnet_fit and not hurnet_layer: hurnet_layer, hurnet_fit = True, False
            is_txt, is_json, text_data = dataset_path.endswith('.txt'), dataset_path.endswith('.json'), ''
            def prepare_json(json_data={}):
                if type(json_data) == dict: pairs = json_data[list(json_data.keys())[0]]
                else: pairs = json_data
                if self.__end_tag is None: self.__end_tag = '<|end|>'
                return '\n\n'.join([str(pair[list(pair.keys())[0]]+'\n'+pair[list(pair.keys())[1]]).replace(self.__end_tag, '').strip()+self.__end_tag for pair in pairs])                
            def is_web_address(url_path=''):
                url_path = str(url_path).lower().strip()
                return url_path.startswith('https://') or url_path.startswith('http://') or url_path.startswith('www.')
            _is_web_address = is_web_address(url_path=dataset_path)
            if _is_web_address:
                is_json = True if '.json' in dataset_path.lower() else False
                def read_remote_file(url_path=''):
                    from urllib.request import urlopen
                    with urlopen(url_path) as response: return str(response.read().decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')).strip()
                text_data = read_remote_file(url_path=dataset_path)
                if is_json:
                    def load_json(string_content=''):
                        json_content = {}
                        string_content = str(string_content)
                        try:
                            from json import loads
                            json_content = loads(string_content)
                        except:
                            from ast import literal_eval
                            json_content = literal_eval(string_content)
                        return json_content
                    json_data = load_json(string_content=text_data)
                    text_data = prepare_json(json_data=json_data)
            else:
                if not is_txt and not is_json and len(self.__string) < 1: raise ValueError('Unsupported file format. Use .txt or .json.')
                if is_txt:
                    with open(dataset_path, 'r', encoding='utf-8') as file: text_data = str(file.read()).strip()
                elif is_json:
                    with open(dataset_path, 'r', encoding='utf-8') as file: json_data = self.__json_load(file)
                    text_data = prepare_json(json_data=json_data)
            if len(self.__string) > 0: text_data += '\n\n' + self.__string
            text_data = text_data.strip()
            sapi_tokenizer = tokenizer == 'sapi'
            if sapi_tokenizer:
                chars = sorted(list(set(text_data)))
                self.__vocab_size = len(chars)
                self.__char_to_idx = {char: index for index, char in enumerate(chars)}
                self.__idx_to_char = {index: char for index, char in enumerate(chars)}
                self.__encode = lambda string: [self.__char_to_idx[char] for char in string]
                self.__decode = lambda indexes: ''.join([self.__idx_to_char[index] for index in indexes])
            else:
                encode = self.__get_encoding('gpt2')
                self.__vocab_size = encode.n_vocab
                self.__encode = encode.encode
                self.__decode = encode.decode
            encoder = self.__encode(text_data)
            data = self.__tensor(encoder, dtype=self.__int64)
            dataset_size = len(data)
            tokens_number = len(encoder)
            if dataset_size < 10: raise ValueError('Dataset too small for training. Add more data.')
            self.__tokenizer = tokenizer
            self.__adjust_hyperparameters(dataset_size, context_window=context_window, tokenizer=tokenizer)
            if validate > 0:
                split_point = int((1-validate) * dataset_size)
                train_data = data[:split_point]
                data_values = data[split_point:]
            else: train_data = data
            if len(train_data) < self.__block_size: self.__block_size = len(train_data) - 1
            train_dataset = self.__TextDataset(train_data, self.__block_size)
            if validate > 0: dataset_values = self.__TextDataset(data_values, self.__block_size)
            train_loader = self.__DataLoader(train_dataset, batch_size=self.__batch_size, shuffle=True)
            if validate > 0 and len(dataset_values) <= 0: loader_values = train_loader
            elif validate > 0: loader_values = self.__DataLoader(dataset_values, batch_size=self.__batch_size, shuffle=False)
            total_steps = len(train_loader) * self.__epochs
            if hurnet_layer: self.__model = self.__TransformerWithHurNet(outer=self, vocab_size=self.__vocab_size, embedding_dim=self.__embedding_dim, number_heads=self.__number_heads, number_layers=self.__number_layers, dropout=self.dropout, block_size=self.__block_size, device=self.__device).to(self.__device)
            else: self.__model = self.__TransformerWithoutHurNet(outer=self, vocab_size=self.__vocab_size, embedding_dim=self.__embedding_dim, number_heads=self.__number_heads, number_layers=self.__number_layers, dropout=self.dropout, block_size=self.__block_size).to(self.__device)
            if not hurnet_fit: self.__optimizer = self.__optim.Adam(self.__model.parameters(), lr=self.__learning_rate)
            if hurnet_initializer:
                self.__model.eval()
                with self.__no_grad():
                    sample_input, sample_target = next(iter(train_loader))
                    sample_input, sample_target = sample_input.to(self.__device), sample_target.to(self.__device)
                    embedded = self.__model.embedding(sample_input)
                    positions = self.__model.positional_encoding[:, :sample_input.size(1), :].to(self.__device)
                    embedded = self.__model.dropout(embedded + positions)
                    mask = self.__triu(self.__ones(sample_input.size(1), sample_input.size(1), device=self.__device) * float('-inf'), diagonal=1)
                    output = self.__model.multi_head_attention(embedded, memory=embedded, tgt_mask=mask)
                    x, y = output.reshape(-1, output.size(-1)), sample_target.reshape(-1)
                    y_onehot, interaction = self.__zeros(y.size(0), self.__vocab_size, device=self.__device).scatter_(1, y.unsqueeze(1), 1), True
                    best_activation = self.__identify_best_activation_function(x=x, y=y_onehot, interaction=interaction)
                    best_bias = self.__identify_best_bias(x=x, y=y_onehot, best_activation=best_activation, interaction=interaction)
                    hook_data, hooks, best_interaction = {}, [], self.__identify_best_interaction(x=x, y=y_onehot, best_activation=best_activation, best_bias=best_bias)
                    def hook_function(module=0, input=[], output=[]): hook_data[module] = (input[0], output)
                    for transformer in self.__model.multi_head_attention.modules():
                        if isinstance(transformer, self.__Linear):
                            hook = transformer.register_forward_hook(hook_function)
                            hooks.append(hook)
                    _ = self.__model(sample_input)
                    for hook in hooks: hook.remove()
                    for module, (X, Y) in hook_data.items():
                        in_features, out_features = X.size(-1), Y.size(-1)
                        temporary_hurnet = self.__HurNetTorch(input_dim=in_features, output_dim=out_features, activation=best_activation, interaction=best_interaction, bias=best_bias, device=self.__device)
                        X_flat, Y_flat = X.reshape(-1, in_features), Y.reshape(-1, out_features)
                        temporary_hurnet.train_layer(x=X_flat, y=Y_flat)
                        new_weight = temporary_hurnet.weights.data[:-2, :].T
                        module.weight.data.copy_(new_weight)
                        if module.bias is not None: module.bias.data.zero_()
                    if hurnet_layer:
                        self.__model.hurnet_layer.activation = best_activation
                        self.__model.hurnet_layer.train_layer(x=x, y=y_onehot)
                    else:
                        initializer_hurnet_layer = self.__HurNetTorch(input_dim=self.__embedding_dim, output_dim=self.__vocab_size, activation=best_activation, interaction=best_interaction, bias=best_bias, device=self.__device)
                        initializer_hurnet_layer.train_layer(x=x, y=y_onehot)
                        with self.__no_grad():
                            hurnet_weights = initializer_hurnet_layer.weights.data[:-2, :]
                            self.__model.output_layer.weight.data.copy_(hurnet_weights.T)
                            self.__model.output_layer.bias.data.zero_()
            feed_forward, Nx, abandon, current_precision, last_val_loss, best_val_loss = True, 0, False, 0.0, 1.0, 1.0
            if progress:
                params_number = sum(parameter.numel() for parameter in self.__model.parameters())
                formatted_tokens, formatted_params = self.__format_numbers(data_number=tokens_number, is_tokens=True), self.__format_numbers(data_number=params_number, is_tokens=False)
                self.parameters_number = params_number
                description = f"Training [{formatted_tokens}/tokens, {formatted_params}/params] - HurNet: [Init: {'ON' if hurnet_initializer else 'OFF'}, Layer: {'ON' if original_hurtnet_layer else 'OFF'}, Fit: {'ON' if original_hurnet_fit else 'OFF'}]"
                progress_bar = self.__tqdm(total=total_steps, desc=description)
            while feed_forward:
                Nx += 1
                self.__model.train()
                for input_batch, target_batch in train_loader:
                    input_batch, target_batch = input_batch.to(self.__device), target_batch.to(self.__device)
                    if hurnet_fit and hurnet_layer and not abandon:
                        with self.__no_grad():
                            embedded = self.__model.embedding(input_batch)
                            positions = self.__model.positional_encoding[:, :input_batch.size(1), :].to(self.__device)
                            embedded = self.__model.dropout(embedded + positions)
                            mask = self.__triu(self.__ones(input_batch.size(1), input_batch.size(1), device=self.__device) * float('-inf'), diagonal=1)
                            output = self.__model.multi_head_attention(embedded, memory=embedded, tgt_mask=mask)
                            x, y = output.reshape(-1, output.size(-1)), target_batch.reshape(-1)
                            y_onehot = self.__zeros(y.size(0), self.__vocab_size, device=self.__device).scatter_(1, y.unsqueeze(1), 1)
                            self.__model.hurnet_layer.train_layer(x=x, y=y_onehot)
                            logistics = self.__model(input_batch)
                            loss = self.__Function.cross_entropy(logistics.reshape(-1, logistics.size(-1)), target_batch.reshape(-1))
                            if Nx > self.__epochs/4 and current_precision < 0.5: abandon, self.__optimizer = True, self.__optim.Adam(self.__model.parameters(), lr=self.__learning_rate)
                    else:
                        self.__optimizer.zero_grad()
                        logistics = self.__model(input_batch)
                        loss = self.__Function.cross_entropy(logistics.reshape(-1, logistics.size(-1)), target_batch.reshape(-1))
                        loss.backward()
                        self.__optimizer.step()
                    loss_item = min((1.0, max((0.0, loss.item()))))
                    current_precision = 1.0-loss_item
                    if progress:
                        progress_bar.set_postfix({'loss': f'{loss_item:.4f}', 'precision': f'{current_precision:.4f}'})
                        progress_bar.update(1)
                    self.__cuda.empty_cache()
                try: last_val_loss = self.__compute_loss(loader_values) if validate > 0 else best_val_loss
                except: last_val_loss = best_val_loss
                if (self.__eval_interval is not None and Nx > 0 and Nx % self.__eval_interval == 0) and (last_val_loss < best_val_loss): best_val_loss = last_val_loss
                if progress: progress_bar.set_postfix({'loss': f'{loss_item:.4f}', 'precision': f'{current_precision:.4f}'})
                if current_precision >= precision or Nx >= self.__epochs:
                    training_metrics['loss'], training_metrics['precision'] = float(loss_item), float(current_precision)
                    break
            if progress:
                progress_bar.update(total_steps)
                progress_bar.close()
            self.__train = True
            val_loss = min((1.0, max((0.0, last_val_loss))))
            generalization_rate = 1-last_val_loss
            training_metrics['val_loss'], training_metrics['generalization_rate'] = float(val_loss), float(generalization_rate)
            return training_metrics
        except Exception as error:
            print('ERROR in train: ' + str(error))
            return {'val_loss': 1.0, 'loss': 1.0, 'generalization_rate': 0.0, 'precision': 0.0}
    def saveModel(self, model_path='', progress=True):
        try:
            model_path = str(model_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if self.__model is None: raise ValueError('Model not initialized. Call train or loadModel first.')
            if len(model_path) > 0:
                directory, file_name = self.__os_path.split(model_path)
                if not file_name: file_name = 'model.gpt'
                elif not file_name.endswith('.gpt'): file_name += '.gpt'
            else: directory, file_name = str(model_path), 'model.gpt'
            if directory and not self.__os_path.exists(directory): self.__os_makedirs(directory)
            save_path = self.__os_path.join(directory, file_name)
            save_dict = {
                'tokenizer': str(self.__tokenizer).lower().strip(),
                'embedding_dim': max((1, int(self.__embedding_dim))) if type(self.__embedding_dim) in (bool, int, float) else -1,
                'vocab_size': max((0, int(self.__vocab_size))) if type(self.__vocab_size) in (bool, int, float) else 0,
                'block_size': max((1, int(self.__block_size))) if type(self.__block_size) in (bool, int, float) else -1,
                'end_tag': str(self.__end_tag) if type(self.__end_tag) is not None else '',
                'number_heads': max((1, int(self.__number_heads))) if type(self.__number_heads) in (bool, int, float) else -1,
                'number_layers': max((1, int(self.__number_layers))) if type(self.__number_layers) in (bool, int, float) else -1,
                'dropout': max((0, int(self.dropout))) if type(self.dropout) in (bool, int, float) else 0.1,
                'parameters_number': max((0, int(self.parameters_number))) if type(self.parameters_number) in (bool, int, float) else 0,
                'architecture_type': 'hur_model',
                'model_state_dict': self.__model.state_dict(),
                'fine_tuning': list(self.__fine_tuning) if type(self.__fine_tuning) in (tuple, list) else [],
                'precision': self.__mean(self.__precisions) if type(self.__precisions) in (tuple, list) and len(self.__precisions) > 0 else 0.5

            }
            if self.__tokenizer == 'sapi':
                save_dict['char_to_idx'] = self.__char_to_idx if type(self.__char_to_idx) == dict else {}
                save_dict['idx_to_char'] = self.__idx_to_char if type(self.__idx_to_char) == dict else {}
            if progress:
                formatted_params = self.__format_numbers(data_number=self.parameters_number, is_tokens=False)
                for _ in self.__tqdm(range(10), desc=f'Saving model with {formatted_params} parameters', leave=False): self.__save(save_dict, save_path)
            else: self.__save(save_dict, save_path)
            self.__train = True
            return True
        except Exception as error:
            print('ERROR in saveModel: ' + str(error))
            return False
    def loadModel(self, model_path='', progress=True):
        try:
            model_path = str(model_path).strip()
            progress = bool(progress) if type(progress) in (bool, int, float) else True
            if len(model_path) > 0:
                directory, file_name = self.__os_path.split(model_path)
                if not file_name: file_name = 'model.gpt'
                elif not file_name.endswith('.gpt'): file_name += '.gpt'
            else: directory, file_name = '', 'model.gpt'
            model_file = self.__os_path.join(directory, file_name)
            if progress:
                for _ in self.__tqdm(range(10), desc='Loading model', leave=False): checkpoint = self.__load(model_file, map_location=self.__device)
            else: checkpoint = self.__load(model_file, map_location=self.__device)
            try: self.__tokenizer = str(checkpoint['tokenizer']).lower().strip()
            except: self.__tokenizer = 'gpt'
            try: self.__embedding_dim = max((1, int(checkpoint['embedding_dim']))) if checkpoint['embedding_dim'] != -1 else None
            except: self.__embedding_dim = None
            try: self.__vocab_size = max((0, int(checkpoint['vocab_size']))) if type(checkpoint['vocab_size']) in (bool, int, float) else 0
            except: self.__vocab_size = 0
            try: self.__block_size = max((1, int(checkpoint['block_size']))) if type(checkpoint['block_size']) != -1 else None
            except: self.__block_size = None
            try: self.__end_tag = str(checkpoint['end_tag'])
            except: self.__end_tag = ''
            try: self.__number_heads = max((1, int(checkpoint['number_heads']))) if type(checkpoint['number_heads']) != -1 else None
            except: self.__number_heads = None
            try: self.__number_layers = max((1, int(checkpoint['number_layers']))) if type(checkpoint['number_layers']) != -1 else None
            except: self.__number_layers = None
            try: self.dropout = max((0, float(checkpoint['dropout']))) if type(checkpoint['dropout']) in (bool, int, float) else 0.1
            except: self.dropout = 0.1
            try: self.parameters_number = max((0, int(checkpoint['parameters_number']))) if type(checkpoint['parameters_number']) in (bool, int, float) else 0
            except: self.parameters_number = 0
            try: self.__fine_tuning = list(checkpoint['fine_tuning']) if type(checkpoint['fine_tuning']) in (tuple, list) else []
            except: self.__fine_tuning = []
            try: self.__precision = min((1, max((0, float(checkpoint['precision']))))) if type(checkpoint['precision']) in (bool, int, float) else 0.5
            except: self.__precision = 0.5
            if self.__tokenizer == 'sapi':
                try: self.__char_to_idx = dict(checkpoint['char_to_idx'])
                except: self.__char_to_idx = {}
                try: self.__idx_to_char = dict(checkpoint['idx_to_char'])
                except: self.__idx_to_char = {}
                self.__encode = lambda string: [self.__char_to_idx[char] for char in string]
                self.__decode = lambda indexes: ''.join([self.__idx_to_char[index] for index in indexes])
            else:
                encode = self.__get_encoding('gpt2')
                self.__encode = encode.encode
                self.__decode = encode.decode
            if len(self.__end_tag) < 1: self.__end_tag = None
            state_dict = checkpoint['model_state_dict']
            has_hurnet = 'hurnet_layer.weights' in state_dict
            if has_hurnet: self.__model = self.__TransformerWithHurNet(outer=self, vocab_size=self.__vocab_size, embedding_dim=self.__embedding_dim, number_heads=self.__number_heads, number_layers=self.__number_layers, dropout=self.dropout, block_size=self.__block_size, device=self.__device).to(self.__device)
            else: self.__model = self.__TransformerWithoutHurNet(outer=self, vocab_size=self.__vocab_size, embedding_dim=self.__embedding_dim, number_heads=self.__number_heads, number_layers=self.__number_layers, dropout=self.dropout, block_size=self.__block_size).to(self.__device)
            self.__model.load_state_dict(state_dict)
            self.__optimizer, self.__train = None, True
            return True
        except Exception as error:
            print('ERROR in loadModel: ' + str(error))
            return False
    def addFit(self, prompt='', answer='', precision=0.5):
        try:
            prompt = str(prompt).strip()
            answer = str(answer).strip()
            precision = min((1, max((0, float(precision))))) if type(precision) in (bool, int, float) else 0.5
            if self.__train:
                prompt = self.__normalize_text(text=prompt)
                embedding = self.__get_encoding('cl100k_base').encode(prompt)
                self.__fine_tuning.append({'embedding': embedding, 'answer': answer})
                self.__precisions.append(precision)
            else:
                if self.__end_tag is None: self.__end_tag = '<|end|>'
                self.__string += prompt+'\n'+answer+self.__end_tag+'\n\n'
            return True
        except Exception as error:
            print('ERROR in addFit: ' + str(error))
            return False
    def predict(self, prompt='', max_tokens=500, temperature=0.5, top_k=0, top_p=1.0, stream=False):
        try:
            prompt = str(prompt).strip()
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 500
            temperature = max((0, float(temperature))) if type(temperature) in (bool, int, float) else 0.5
            top_k = max((0, int(top_k))) if type(top_k) in (bool, int, float) else 0
            top_p = min((1.0, max((0.0, int(top_p))))) if type(top_p) in (bool, int, float) else 1.0
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            if self.__model is None: raise ValueError('Model not initialized. Call train or loadModel first.')
            if stream: return self.__generate_tokens(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p, end_tag=self.__end_tag)
            tokens = list(self.__generate_tokens(prompt=prompt, max_tokens=max_tokens, temperature=temperature, top_k=top_k, top_p=top_p, end_tag=self.__end_tag))
            decoded_tokens = ''.join(tokens)
            if self.__end_tag is not None and self.__end_tag in decoded_tokens: decoded_tokens = decoded_tokens.split(self.__end_tag)[0].strip()
            return decoded_tokens.strip()
        except Exception as error:
            print('ERROR in predict: ' + str(error))
            return ''
    def print_predict(self, prompt='', max_tokens=500, temperature=0.5, top_k=0, top_p=1.0, stream=False):
        try:
            prompt = str(prompt).strip()
            max_tokens = max((1, int(max_tokens))) if type(max_tokens) in (bool, int, float) else 500
            temperature = max((0, float(temperature))) if type(temperature) in (bool, int, float) else 0.5
            top_k = max((0, int(top_k))) if type(top_k) in (bool, int, float) else 0
            top_p = min((1.0, max((0.0, int(top_p))))) if type(top_p) in (bool, int, float) else 1.0
            stream = bool(stream) if type(stream) in (bool, int, float) else False
            if self.__model is None: raise ValueError('Model not initialized. Call train or loadModel first.')
            token_generator = self.predict(prompt=prompt, max_tokens=max_tokens, temperature=temperature, stream=stream)
            if stream:
                for token in token_generator: print(token, end='', flush=True)
                print()
            else: print(token_generator)
        except Exception as error:
            print('ERROR in print_predict: ' + str(error))
# THIS IS AN EXTENSION NETWORK OF THE SKILLS OF THE HURNET ARTIFICIAL NEURAL NETWORK
# The HurModel (Hur of HurNet and Model of language model) is a sophisticated artificial neural network computational algorithm that proposes a new architecture for language models based on Transformers.
# This architecture uses aspects already known from Transformers applied to GPT models, such as normalizers, tokenizers, embeddings and attention mechanisms,
# but adds new concepts such as intelligent initialization of weights using layers of the HurNet network, insertion of auxiliary HurNet layers and use of HurNet networks in the final adjustment of weights.
# As an integral part of the architecture, HurModel models do not require hyperparameter configurations, since this can be done completely autonomously without developer intervention,
# allowing the programmer to focus only on the data that is the most important part of the model. All these features make the HurModel language model architecture superior to the already known GPT models.
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
